#!/usr/bin/env python3
"""
Wind Module Renderer för E-Paper Väderstation - HORISONTELL CYKEL-OPTIMERAD LAYOUT
Visar vindstyrka + vindriktning med fokus på snabba cykel-beslut

HORISONTELL cykel-fokuserad layout (optimal utrymmesutnyttjande):
🌪️ 4.8 m/s      ← Ikon + M/S på samma rad (effektivt)
   Måttlig vind  ← Svensk benämning under
   
   ↙️ SV         ← Pil-ikon + kort riktning längst ner

Ikoner:
- wi-strong-wind.png (generell vind-ikon från system/, till vänster om M/S)
- wi-wind-[direction].png (pil-ikon från wind/, med kort svenska förkortningar)
"""

from typing import Dict, List
from .base_renderer import ModuleRenderer

class WindRenderer(ModuleRenderer):
    """
    Renderer för wind-modul med HORISONTELL CYKEL-FOKUSERAD layout
    
    Visar:
    - Generell vind-ikon (wi-strong-wind.png) till VÄNSTER om M/S-värdet
    - M/S-värde PROMINENT på samma rad som ikonen (effektiv layout)
    - Svensk vindbenämning (under M/S-värdet)
    - Kort vindriktning (SV, NO, etc.) med pil-ikon längst ner
    - Horisontell layout för optimal E-Paper utrymmesutnyttjande (240×200px)
    """
    
    def render(self, x: int, y: int, width: int, height: int, 
               weather_data: Dict, context_data: Dict) -> bool:
        """
        Rendera wind-modul med HORISONTELL layout
        
        Args:
            x, y: Position på canvas
            width, height: Modulens storlek (240×200px för MEDIUM 1)
            weather_data: Väderdata från weather_client
            context_data: Trigger context data
            
        Returns:
            True om rendering lyckades
        """
        try:
            self.logger.info(f"🌬️ Renderar HORISONTELL wind-modul ({width}×{height})")
            
            # Hämta vinddata med säker fallback
            wind_speed = self.safe_get_value(weather_data, 'wind_speed', 0.0, float)
            wind_direction = self.safe_get_value(weather_data, 'wind_direction', 0.0, float)
            
            # Konvertera till svenska beskrivningar
            speed_description = self.icon_manager.get_wind_description_swedish(wind_speed)
            direction_short, cardinal_code = self.icon_manager.get_wind_direction_info(wind_direction)
            
            # === HORISONTELL CYKEL-FOKUSERAD LAYOUT ===
            
            # 1. Generell vind-ikon (till vänster, samma rad som M/S)
            general_wind_icon = self.icon_manager.get_system_icon('strong-wind', size=(48, 48))
            icon_x = x + 20  # Fast position till vänster
            icon_y = y + 25  # Höjd för att centrera med text
            if general_wind_icon:
                self.paste_icon_on_canvas(general_wind_icon, icon_x, icon_y)
            
            # 2. M/S-värde (STORT, till höger om ikon på samma rad)
            ms_text = f"{wind_speed:.1f} m/s"
            ms_x = icon_x + 60  # 60px till höger om ikon (48px + 12px mellanrum)
            ms_y = y + 35       # Centrerad vertikalt med ikonen
            self.draw_text_with_fallback(
                (ms_x, ms_y),
                ms_text,
                self.fonts.get('hero_temp', self.fonts.get('small_main')),  # STOR font!
                fill=0
            )
            
            # 3. Vindbenämning (under M/S-värdet, indenterat för läsbarhet)
            desc_x = ms_x  # Samma X som M/S-värdet för alignment
            desc_y = ms_y + 50  # 50px under M/S-värdet
            self.draw_text_with_fallback(
                (desc_x, desc_y),
                speed_description,
                self.fonts.get('medium_desc', self.fonts.get('small_desc')),
                fill=0
            )
            
            # 4. Pil-ikon för riktning (längst ner, till vänster)
            cardinal_icon = self.icon_manager.get_wind_icon(cardinal_code, size=(32, 32))
            cardinal_x = x + 30  # Lite indenterat från vänsterkant
            cardinal_y = y + height - 50  # 50px från botten
            if cardinal_icon:
                self.paste_icon_on_canvas(cardinal_icon, cardinal_x, cardinal_y)
            
            # 5. Kort vindriktning (till höger om pil-ikon)
            direction_x = cardinal_x + 40  # 40px till höger om pil-ikon
            direction_y = cardinal_y + 5   # Lite justerad för vertikal centrering
            self.draw_text_with_fallback(
                (direction_x, direction_y),
                direction_short,
                self.fonts.get('medium_desc', self.fonts.get('small_desc')),
                fill=0
            )
            
            self.logger.info(f"✅ HORISONTELL cykel-optimerad wind-modul rendered: {wind_speed:.1f}m/s {speed_description}, {direction_short}")
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
                'HORISONTELL CYKEL-FOKUSERAD layout för optimal utrymmesutnyttjande',
                'Generell vind-ikon + M/S-värde på SAMMA RAD (effektiv design)',
                'M/S-värde PROMINENT (hero_temp font) - huvuddata för cykling',
                'Korta svenska vindförkortningar (SV, NO, etc.) från kompass',
                'Pil-ikon för exakt vindriktning från wind-biblioteket',
                'Horisontell layout sparar utrymme på E-Paper (240×200px)',
                'Vindstyrka enligt "Benämning på land" för kontext',
                'FÖRBÄTTRAD: Ikon + M/S samma rad istället för slöseri med vertikal layout'
            ]
        })
        return info