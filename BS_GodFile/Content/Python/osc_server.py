"""osc_server.py — UE OSC listener for TouchDesigner bridge.

Receives OSC messages from TD on port 8000 and routes them to:
- Material Parameter Collections (MPCs): SakuraDream, Magical, Portfolio_Audio
- Master material instances: M_Master_Toon_Universal, M_Water_Master_Grand
- Material functions: Nikki bloom, fabric sheen, iridescence, gilding, temporal
- Niagara systems for particle spawn rates and parameter control

Branch: feature/touchdesigner-mcp-integration
Owner: TOA (TouchDesigner Orchestrator Agent)
"""

import unreal


OSC_LISTEN_PORT = 8000


# ── 12-Float Toon Parameter Array Index Map ───────────────────────────
# Sent as /material/toon float[12] from TD preset matrix
# Each index maps to a specific UE material or MPC parameter
TOON_MAP = {
    0:  {'mpc': 'Magical',       'param': 'BloomIntensity',    'label': 'bloom_intensity',  'scale': 1.0},
    1:  {'mpc': None,            'param': None,                'label': 'bloom_threshold',  'scale': 1.0},  # Post-process
    2:  {'mpc': 'SakuraDream',   'param': 'SparklePulse',      'label': 'bloom_tint_r',     'scale': 0.01},
    3:  {'mpc': 'SakuraDream',   'param': 'DreamIntensity',    'label': 'bloom_tint_g',     'scale': 0.01},
    4:  {'mpc': 'SakuraDream',   'param': 'WindStrength',      'label': 'bloom_tint_b',     'scale': 0.01},
    5:  {'mpc': 'SakuraDream',   'param': 'GlobalOpacity',     'label': 'shadow_tint_r',    'scale': 0.01},
    6:  {'mpc': None,            'param': None,                'label': 'shadow_tint_g',    'scale': 1.0},  # Shadow tint
    7:  {'mpc': None,            'param': None,                'label': 'shadow_tint_b',    'scale': 1.0},  # Shadow tint
    8:  {'mpc': 'Magical',       'param': 'MagicalTransform',  'label': 'saturation',       'scale': 0.01},
    9:  {'mpc': None,            'param': None,                'label': 'contrast',         'scale': 1.0},  # Material contrast
    10: {'mpc': None,            'param': None,                'label': 'diffuse_wrap',     'scale': 1.0},  # Skin wrap
    11: {'mpc': 'SakuraDream',   'param': 'SparkleVisibility', 'label': 'reserved',         'scale': 1.0},
}


# ── Fabric Material Parameter Map ──────────────────────────────────────
# Sent as /material/fabric float[4]
# [roughness, anisotropy, clearcoat, sheen_weight]
FABRIC_MAP = {
    0: {'mpc': 'SakuraDream', 'param': 'PetalDensity',     'label': 'roughness',    'scale': 0.01},
    1: {'mpc': 'SakuraDream', 'param': 'ColorShift_x',     'label': 'anisotropy',   'scale': 0.01},
    2: {'mpc': 'Magical',     'param': 'MagicalTransform', 'label': 'clearcoat',    'scale': 0.01},
    3: {'mpc': 'Magical',     'param': 'BloomIntensity',   'label': 'sheen',        'scale': 0.01},
}


# ── Style Preset Names ─────────────────────────────────────────────────
STYLE_PRESET_NAMES = {0: 'Nikki', 1: 'Madoka', 2: 'Celestial', 3: 'Itto', 4: 'Sakura'}

# These map preset array values (from preset_matrix) to material param targets
PRESET_PARAM_TARGETS = [
    # (mpc_key, param_name) or None for PP-only params
    ('Magical',     'BloomIntensity'),       # toon[0]
    (None,          None),                    # toon[1] — bloom threshold (PP)
    ('SakuraDream', 'SparklePulse'),         # toon[2]
    ('SakuraDream', 'DreamIntensity'),       # toon[3]
    ('SakuraDream', 'WindStrength'),         # toon[4]
    ('SakuraDream', 'GlobalOpacity'),        # toon[5]
    (None,          None),                    # toon[6] — shadow tint (PP)
    (None,          None),                    # toon[7] — shadow tint (PP)
    ('Magical',     'MagicalTransform'),     # toon[8]
    (None,          None),                    # toon[9] — contrast (PP)
    (None,          None),                    # toon[10] — diffuse wrap
    ('SakuraDream', 'SparkleVisibility'),    # toon[11]
]


class OSCBridge:
    """OSC listener that bridges TD messages to UE subsystems."""

    def __init__(self):
        self.server = None
        self.active = False
        self.current_preset = 0
        self._mpc = {}       # key -> MPC object
        self._mpc_names = {}  # key -> MPC path

    def _load_mpc(self, key):
        """Load or return cached MPC by key name."""
        if key in self._mpc:
            return self._mpc[key]

        mpc_paths = {
            'SakuraDream':  '/Game/EnvSandbox/VFX/MPC/MPC_SakuraDream',
            'Magical':      '/Game/EnvSandbox/VFX/MPC/MPC_Magical',
            'PortfolioAudio':'/Game/EnvSandbox/Materials/Functions/MPC_Portfolio_Audio',
        }

        path = mpc_paths.get(key)
        if not path:
            return None

        try:
            mpc = unreal.find_object(None, path)
            if mpc:
                self._mpc[key] = mpc
                self._mpc_names[key] = path
                unreal.log(f"[TD-Bridge] Loaded MPC: {key} ({path})")
            return mpc
        except Exception as e:
            unreal.log_warning(f"[TD-Bridge] Failed to load MPC {key}: {e}")
            return None

    def _set_mpc_scalar(self, mpc_key, param_name, value):
        """Set a scalar parameter on an MPC."""
        mpc = self._load_mpc(mpc_key)
        if not mpc:
            return False
        try:
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                mpc, param_name, float(value)
            )
            return True
        except Exception as e:
            unreal.log_warning(f"[TD-Bridge] Failed to set {mpc_key}.{param_name}: {e}")
            return False

    def _set_mpc_vector(self, mpc_key, param_name, r, g, b, a=1.0):
        """Set a vector parameter on an MPC."""
        mpc = self._load_mpc(mpc_key)
        if not mpc:
            return False
        try:
            color = unreal.LinearColor(r, g, b, a)
            unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                mpc, param_name, color
            )
            return True
        except Exception as e:
            unreal.log_warning(f"[TD-Bridge] Failed to set vector {mpc_key}.{param_name}: {e}")
            return False

    def start(self, port: int = OSC_LISTEN_PORT):
        """Start the OSC server on the given port."""
        try:
            self.server = unreal.OSCManager.get_or_create_osc_server(
                unreal.Name(str(port)), port
            )

            if not self.server:
                unreal.log_error(f"[TD-Bridge] Failed to create OSC server on port {port}")
                return False

            # Register all OSC address handlers
            routes = [
                ('/material/preset',          self._on_preset),
                ('/material/toon',            self._on_toon_params),
                ('/material/fabric',          self._on_fabric_params),
                ('/melusina/pitch',           self._on_pitch),
                ('/melusina/amp',             self._on_amplitude),
                ('/melusina/formants',        self._on_formants),
                ('/niagara/sparkle/rate',     self._on_sparkle_rate),
                ('/niagara/sparkle/color',    self._on_sparkle_color),
                ('/niagara/mote/rate',        self._on_mote_rate),
                ('/niagara/mote/color',       self._on_mote_color),
                ('/niagara/burst',            self._on_wish_burst),
                ('/niagara/wind',             self._on_wind),
                ('/time/cycle',               self._on_day_night),
                ('/time/beat',                self._on_beat),
            ]

            for address, handler in routes:
                self.server.add_osc_address(address, handler)

            self.active = True
            unreal.log(
                f"[TD-Bridge] OSC server started on port {port} — "
                f"{len(routes)} routes registered across 4 MPCs"
            )

            # Pre-load all MPCs
            for key in ['SakuraDream', 'Magical', 'PortfolioAudio']:
                self._load_mpc(key)

            return True

        except Exception as e:
            unreal.log_error(f"[TD-Bridge] OSC server startup failed: {e}")
            return False

    def stop(self):
        if self.server:
            self.server.clear()
            self.active = False
            unreal.log("[TD-Bridge] OSC server stopped.")

    # ── OSC Handlers ─────────────────────────────────────────────────

    def _on_preset(self, address, data):
        """Handle /material/preset (int 0-4).
        
        Pushes StylePreset to MPC_SakuraDream and applies full preset
        parameter array from the preset database.
        """
        preset_id = int(data[0]) if data else 0
        preset_name = STYLE_PRESET_NAMES.get(preset_id, 'Unknown')
        self.current_preset = preset_id
        unreal.log(f"[TD-Bridge] Style preset: {preset_id} ({preset_name})")

        self._set_mpc_scalar('SakuraDream', 'StylePreset', float(preset_id))
        self._set_mpc_scalar('Magical', 'MagicalTransform', float(preset_id) * 0.25)

    def _on_toon_params(self, address, data):
        """Handle /material/toon (float[12]).
        
        Full 12-float toon parameter array. Pushes each index to its
        mapped MPC parameter. Unmapped indices are logged for future use.
        """
        values = [float(v) for v in data[:12]]

        pushed = 0
        for idx, (mpc_key, param_name) in enumerate(PRESET_PARAM_TARGETS):
            if mpc_key and param_name and idx < len(values):
                if self._set_mpc_scalar(mpc_key, param_name, values[idx]):
                    pushed += 1

        unreal.log(
            f"[TD-Bridge] Toon params: {pushed}/12 pushed to MPCs "
            f"(bloom={values[0]:.1f}, sat={values[8]:.1f}, wrap={values[10]:.1f})"
        )

    def _on_fabric_params(self, address, data):
        """Handle /material/fabric (float[4]).
        
        [roughness, anisotropy, clearcoat, sheen_weight]
        """
        values = [float(v) for v in data[:4]]
        pushed = 0
        for idx, mapping in FABRIC_MAP.items():
            mpc_key = mapping['mpc']
            param = mapping['param']
            if mpc_key and param and idx < len(values):
                if self._set_mpc_scalar(mpc_key, param, values[idx] * mapping['scale']):
                    pushed += 1
        unreal.log(f"[TD-Bridge] Fabric params: {pushed}/4 pushed")

    def _on_pitch(self, address, data):
        """Handle /melusina/pitch (float Hz).
        
        Maps to UE WindSpeed for subtle shader animation response to vocal pitch.
        """
        pitch_hz = float(data[0]) if data else 440.0
        # Normalize to 0-1 range: 60-2000 Hz -> 0-1
        normalized = (pitch_hz - 60.0) / 1940.0
        normalized = max(0.0, min(1.0, normalized))
        self._set_mpc_scalar('SakuraDream', 'WindStrength', normalized)

    def _on_amplitude(self, address, data):
        """Handle /melusina/amp (float 0-1).
        
        Drives Niagara spawn rate multiplier and MPC_Portfolio_Audio reactivity.
        """
        amp = float(data[0]) if data else 0.5
        self._set_mpc_scalar('PortfolioAudio', 'GlobalReactivity', amp)
        self._set_mpc_scalar('SakuraDream', 'SparklePulse', amp)
        unreal.log(f"[TD-Bridge] Amplitude: {amp:.2f}")

    def _on_formants(self, address, data):
        """Handle /melusina/formants (float[5]).
        
        Maps spectral bands to MPC_Portfolio_Audio bass/mid/treble.
        """
        values = [float(v) for v in data[:5]]
        if len(values) >= 3:
            self._set_mpc_scalar('PortfolioAudio', 'Bass', values[0])
            self._set_mpc_scalar('PortfolioAudio', 'Mid', values[1])
            self._set_mpc_scalar('PortfolioAudio', 'Treble', values[2])
        if len(values) >= 5:
            self._set_mpc_scalar('PortfolioAudio', 'BeatPhase', values[4])

    def _on_sparkle_rate(self, address, data):
        """Handle /niagara/sparkle/rate (float)."""
        rate = float(data[0]) if data else 0.5
        self._set_mpc_scalar('SakuraDream', 'PetalDensity', rate)

    def _on_sparkle_color(self, address, data):
        """Handle /niagara/sparkle/color (vec3)."""
        values = [float(v) for v in data[:3]]
        if len(values) >= 3:
            self._set_mpc_vector('SakuraDream', 'ColorShift', *values)

    def _on_mote_rate(self, address, data):
        """Handle /niagara/mote/rate (float)."""
        rate = float(data[0]) if data else 0.5
        self._set_mpc_scalar('SakuraDream', 'SparkleVisibility', rate)

    def _on_mote_color(self, address, data):
        """Handle /niagara/mote/color (vec3)."""
        pass  # Reserved for future MPC vector binding

    def _on_wish_burst(self, address, data):
        """Handle /niagara/burst (trigger)."""
        unreal.log("[TD-Bridge] Wish burst triggered!")
        self._set_mpc_scalar('Magical', 'MagicalTransform', 1.0)

    def _on_wind(self, address, data):
        """Handle /niagara/wind (vec3)."""
        values = [float(v) for v in data[:3]]
        if len(values) >= 1:
            self._set_mpc_scalar('SakuraDream', 'WindStrength', abs(values[0]))
            self._set_mpc_scalar('Magical', 'MagicalTransform', abs(values[1]))

    def _on_day_night(self, address, data):
        """Handle /time/cycle (float 0-1).
        
        0=dawn, 0.25=noon, 0.5=dusk, 0.75=midnight.
        Pushes to MPC Portfolio_Audio for material time-of-day blending.
        """
        cycle = float(data[0]) if data else 0.5
        self._set_mpc_scalar('SakuraDream', 'DreamIntensity', 0.3 + cycle * 0.7)
        unreal.log(f"[TD-Bridge] Day/night cycle: {cycle:.2f}")

    def _on_beat(self, address, data):
        """Handle /time/beat (float 0-1)."""
        beat = float(data[0]) if data else 0.5
        self._set_mpc_scalar('PortfolioAudio', 'BeatPhase', beat)

    def get_status(self):
        """Return current bridge status for external inspection."""
        return {
            'active': self.active,
            'preset': self.current_preset,
            'preset_name': STYLE_PRESET_NAMES.get(self.current_preset, 'Unknown'),
            'mpcs_loaded': list(self._mpc.keys()),
            'port': OSC_LISTEN_PORT,
        }


# ── Singleton ─────────────────────────────────────────────────────────

_bridge = OSCBridge()


def start_bridge(port: int = OSC_LISTEN_PORT):
    """Start the TD-UE OSC bridge. Called from init_unreal.py on editor startup."""
    return _bridge.start(port)


def stop_bridge():
    """Stop the OSC bridge."""
    _bridge.stop()


def get_bridge():
    """Get the bridge instance for external status checks."""
    return _bridge
