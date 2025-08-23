#!/usr/bin/env python3
"""
Wind Module Renderer för E-Paper Väderstation - SYMMETRISK CYKEL-OPTIMERAD LAYOUT
Visar vindstyrka + vindriktning med fokus på snabba cykel-beslut

FIXAD SYMMETRISK layout (som andra moduler):
┌─────────────────────┐
│      🌪️             │
│                     │
│   5.3 m/s           │ ← HUVUDDATA PROMINENT
│   Måttlig vind      │ ← BESKRIVANDE TEXT BALANSERAD
│                     │
│      ↗️ N           │ ← SEKUNDÄRDATA DISKRET
└─────────────────────┘

FIXAR:
✅ Modulram (som andra moduler har)
✅ Balanserade element (lagom storlekar)
✅ Symmetrisk centrering
✅ M/S + beskrivning som HUVUDDATA
✅ Vindriktning som sekundärdata
"""

from typing import Dict, List
from .base_renderer import ModuleRenderer

class WindRenderer(ModuleRenderer):
    """
    Renderer för wind-modul med SYMMETRISK CYKEL-FOKUSERAD layout
    
    FIXAR alla layout-problem:
    - Lägger till modulram (som andra moduler)
    - Balanserar element-storlekar
    - Centrerar allt symmetriskt
    - Gör M/S + beskrivning till HUVUDDATA
    - Vindriktning som diskret sekundärdata
    """
    
    def render(self, x: int, y: int, width: int, height: int, 
               weather_data: Dict, context_data: Dict) -> bool:
        """
        Rendera wind-modul med FIXAD SYMMETRISK layout
        
        Args:
            x, y: Position på canvas
            width, height: Modulens storlek (240×200px för MEDIUM 1)
            weather_data: Väderdata från weather_client
            context_data: Trigger context data
            
        Returns:
            True om rendering lyckades
        """
        try:
            self.logger.info(f"🌬️ Renderar FIXAD SYMMETRISK wind-modul ({width}×{height})")
            
            # Hämta vinddata med säker fallback
            wind_speed = self.safe_get_value(weather_data, 'wind_speed', 0.0, float)
            wind_direction = self.safe_get_value(weather_data, 'wind_direction', 0.0, float)
            
            # Konvertera till svenska beskrivningar
            speed_description = self.icon_manager.get_wind_description_swedish(wind_speed)
            direction_short, cardinal_code = self.icon_manager.get_wind_direction_info(wind_direction)
            
            # === MODULRAM (som andra moduler har) ===
            self.draw.rectangle(
                [(x + 2, y + 2), (x + width - 2, y + height - 2)],
                outline=0,
                width=2
            )
            
            # === SYMMETRISK CENTRERAD LAYOUT ===
            
            # Beräkna center för symmetrisk layout
            center_x = x + width // 2
            
            # 1. ALLMÄN VINDIKON (överst, centrerad, lagom storlek)
            general_wind_icon = self.icon_manager.get_system_icon('strong-wind', size=(40, 40))  # Lagom storlek
            if general_wind_icon:
                icon_x = center_x - 20  # Centrerad (40px/2 = 20px offset)
                icon_y = y + 25
                self.paste_icon_on_canvas(general_wind_icon, icon_x, icon_y)
            
            # 2. HUVUDDATA: M/S-VÄRDE (prominent men får plats)
            ms_text = f"{wind_speed:.1f} m/s"
            text_bbox = self.get_text_bounds(ms_text, self.fonts.get('large_main', self.fonts.get('medium_main')))
            ms_x = center_x - text_bbox[0] // 2  # Centrerad
            ms_y = y + 80  # Under ikonen
            self.draw_text_with_fallback(
                (ms_x, ms_y),
                ms_text,
                self.fonts.get('large_main', self.fonts.get('medium_main')),  # Lagom font för att få plats
                fill=0
            )
            
            # 3. HUVUDDATA: BESKRIVANDE TEXT (balanserad storlek)
            desc_bbox = self.get_text_bounds(speed_description, self.fonts.get('medium_main', self.fonts.get('small_main')))
            desc_x = center_x - desc_bbox[0] // 2  # Centrerad
            desc_y = ms_y + 40  # Under M/S-värdet
            self.draw_text_with_fallback(
                (desc_x, desc_y),
                speed_description,
                self.fonts.get('medium_main', self.fonts.get('small_main')),  # Balanserad storlek
                fill=0
            )
            
            # 4. SEKUNDÄRDATA: PIL-IKON för riktning (längst ner, centrerad men diskret)
            cardinal_icon = self.icon_manager.get_wind_icon(cardinal_code, size=(24, 24))  # Diskret storlek
            direction_y_base = y + height - 45  # Från botten
            
            # Kombinerad bredd för pil + text för centrering
            direction_text_bbox = self.get_text_bounds(direction_short, self.fonts.get('small_main', self.fonts.get('small_desc')))
            combined_width = 24 + 8 + direction_text_bbox[0]  # ikon + mellanrum + text
            combined_x = center_x - combined_width // 2
            
            if cardinal_icon:
                self.paste_icon_on_canvas(cardinal_icon, combined_x, direction_y_base)
            
            # 5. SEKUNDÄRDATA: Kort vindriktning (diskret, bredvid pil)
            direction_x = combined_x + 24 + 8  # Efter pil-ikon + mellanrum
            direction_y = direction_y_base + 2   # Lite justerad för vertikal centrering
            self.draw_text_with_fallback(
                (direction_x, direction_y),
                direction_short,
                self.fonts.get('small_main', self.fonts.get('small_desc')),  # Diskret storlek
                fill=0
            )
            
            self.logger.info(f"✅ FIXAD SYMMETRISK cykel-optimerad wind-modul: {wind_speed:.1f}m/s {speed_description}, {direction_short}")
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
                '✅ FIXAD LAYOUT: Modulram som andra moduler',
                '✅ SYMMETRISK CENTRERING: Alla element balanserade',
                '✅ HUVUDDATA PROMINENT: M/S + beskrivning som fokus',
                '✅ LAGOM STORLEKAR: Ikoner och text får plats i modulen',
                '✅ SEKUNDÄRDATA DISKRET: Vindriktning mindre men synlig',
                '✅ CYKEL-OPTIMERAD: Snabb avläsning för cykel-beslut',
                'M/S-värde LAGOM STORT (large_main font) - får plats i ram',
                'Beskrivande text BALANSERAD (medium_main font)',
                'Allmän vindikon LAGOM (40px) - synlig men tar inte över',
                'Vindriktning DISKRET (24px pil + small_main text)',
                'Korta svenska vindförkortningar (SV, NO, etc.)',
                'Symmetrisk centrering för professionell look som andra moduler'
            ]
        })
        return info