#!/usr/bin/env python3
"""
Wind Module Renderer för E-Paper Väderstation - CYKEL-OPTIMERAD LAYOUT
Visar vindstyrka + vindriktning med fokus på snabba cykel-beslut

Cykel-fokuserad layout:
🌪️       4.8 m/s
      Måttlig vind
      
         ↙️ SV

Ikoner:
- wi-strong-wind.png (generell vind-ikon från system/, centrerad överst)
- wi-wind-[direction].png (pil-ikon från wind/, med kort svenska förkortningar)
"""

from typing import Dict, List
from .base_renderer import ModuleRenderer

class WindRenderer(ModuleRenderer):
    """
    Renderer för wind-modul med CYKEL-FOKUSERAD layout
    
    Visar:
    - Generell vind-ikon (wi-strong-wind.png från system/, centrerad överst)
    - M/S-värde PROMINENT för snabba cykel-beslut
    - Svensk vindbenämning (mindre, under m/s-värdet)
    - Kort vindriktning (SV, NO, etc.) med pil-ikon från wind/
    - Centrerad layout optimerad för cykling (240×200px)
    """
    
    def render(self, x: int, y: int, width: int, height: int, 
               weather_data: Dict, context_data: Dict) -> bool:
        """
        Rendera wind-modul
        
        Args:
            x, y: Position på canvas
            width, height: Modulens storlek (240×200px för MEDIUM 1)
            weather_data: Väderdata från weather_client
            context_data: Trigger context data
            
        Returns:
            True om rendering lyckades
        """
        try:
            self.logger.info(f"🌬️ Renderar wind-modul ({width}×{height})")
            
            # Hämta vinddata med säker fallback
            wind_speed = self.safe_get_value(weather_data, 'wind_speed', 0.0, float)
            wind_direction = self.safe_get_value(weather_data, 'wind_direction', 0.0, float)
            
            # Konvertera till svenska beskrivningar
            speed_description = self.icon_manager.get_wind_description_swedish(wind_speed)
            direction_short, cardinal_code = self.icon_manager.get_wind_direction_info(wind_direction)
            
            # === CYKEL-FOKUSERAD CENTRERAD LAYOUT ===
            
            # 1. Generell vind-ikon (centrerad överst)
            general_wind_icon = self.icon_manager.get_system_icon('strong-wind', size=(48, 48))
            icon_center_x = x + (width // 2) - 24  # Centrera ikon (48px bred)
            if general_wind_icon:
                self.paste_icon_on_canvas(general_wind_icon, icon_center_x, y + 15)
            
            # 2. M/S-värde (STORT, prominent, centrerat under ikon)
            ms_text = f"{wind_speed:.1f} m/s"
            ms_center_x = x + (width // 2)  # Centrera text
            self.draw_text_with_fallback(
                (ms_center_x - 50, y + 75),  # Justera X för att centrera (ungefär)
                ms_text,
                self.fonts.get('hero_temp', self.fonts.get('small_main')),  # STOR font!
                fill=0
            )
            
            # 3. Vindbenämning (mindre, centrerad under m/s)
            desc_center_x = x + (width // 2)
            self.draw_text_with_fallback(
                (desc_center_x - 40, y + 115),  # Justera X för att centrera
                speed_description,
                self.fonts.get('medium_desc', self.fonts.get('small_desc')),
                fill=0
            )
            
            # 4. Pil-ikon för riktning (centrerad, under beskrivning)
            cardinal_icon = self.icon_manager.get_wind_icon(cardinal_code, size=(32, 32))
            cardinal_center_x = x + (width // 2) - 16  # Centrera ikon (32px bred)
            if cardinal_icon:
                self.paste_icon_on_canvas(cardinal_icon, cardinal_center_x, y + 150)
            
            # 5. Kort vindriktning (bredvid pil-ikon)
            direction_x = cardinal_center_x + 40  # Till höger om pil-ikon
            self.draw_text_with_fallback(
                (direction_x, y + 155),
                direction_short,
                self.fonts.get('medium_desc', self.fonts.get('small_desc')),
                fill=0
            )
            
            self.logger.info(f"✅ Cykel-optimerad wind-modul rendered: {wind_speed:.1f}m/s {speed_description}, {direction_short}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Fel vid wind rendering: {e}")
            return self.render_fallback_content(
                x, y, width, height, 
                "Wind-data ej tillgänglig"
            )
    
    def get_required_data_sources(self) -> List[str]:
        """Wind-modul behöver SMHI prognosdata för vindstyrka och vindriktning"""
        return ['smhi']
    
    def get_module_info(self) -> Dict:
        """Metadata för wind-modul"""
        info = super().get_module_info()
        info.update({
            'purpose': 'Visa vindstyrka och vindriktning med svenska benämningar',
            'data_sources': ['SMHI vindprognoser (ws + wd parametrar)'],
            'layout': 'Ersätter barometer-modulen (MEDIUM 1 position)',
            'features': [
                'CYKEL-FOKUSERAD layout för snabba wind-beslut',
                'M/S-värde PROMINENT (hero_temp font) - huvuddata',
                'Generell vind-ikon (wi-strong-wind.png) centrerad överst',
                'Korta svenska vindförkortningar (SV, NO, etc.) från kompass',
                'Pil-ikon för exakt vindriktning från wind-biblioteket',
                'Centrerad layout utan tekniska detaljer (inga grader/datakälla)',
                'Optimal utnyttjande av E-Paper skärmyta (240×200px)',
                'Vindstyrka enligt "Benämning på land" för kontext'
            ]
        })
        return info