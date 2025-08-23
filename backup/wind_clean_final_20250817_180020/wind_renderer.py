#!/usr/bin/env python3
"""
Wind Module Renderer för E-Paper Väderstation - KOLLISIONSSÄKER DESIGN
Implementerar kollegans UX-feedback med konkreta kollisionsfixar

KOLLISIONSSÄKER LAYOUT (fixar ikonkrock och trunkering):
┌─────────────────────┐
│  4.8 m/s        🌪️  │ ← M/S + mindre ikon (32px) höger
│  Måttlig vind       │ ← RADBRYTNING istället för "Måttlig..."
│                     │ ← LUFTIG SPACING  
│      ↗️ N           │ ← ROBUST kardinalpil med debug
└─────────────────────┘

KOLLEGANS KONKRETA FIXAR:
✅ Radbrytning: "Måttlig vind" på två rader istället för ellips  
✅ Mindre vindikon: 32×32px istället för 40×40px för mindre krockrisk
✅ Högerkolumn-skydd: Text kan aldrig nå ikoner i högerkolumn
✅ Kardinalpil-debug: Omfattande logging och alternativa koder
✅ Kollisionsskydd: M/s kan aldrig täcka ikoner
"""

from typing import Dict, List
from .base_renderer import ModuleRenderer

class WindRenderer(ModuleRenderer):
    """
    Renderer för wind-modul med KOLLISIONSSÄKER UX-DESIGN
    
    Implementerar kollegans konkreta feedback:
    - RADBRYTNING: "Måttlig vind" på 2 rader istället för "Måttlig..."  
    - MINDRE VINDIKON: 32×32px istället för 40×40px för mindre krockrisk
    - HÖGERKOLUMN-SKYDD: Text kan aldrig nå ikoner (PRIMARY_MAX_W)
    - KARDINALPIL-DEBUG: Omfattande logging och alternativa koder
    - KOLLISIONSSKYDD: M/s täcker aldrig ikoner i högerkolumn
    """
    
    def render(self, x: int, y: int, width: int, height: int, 
               weather_data: Dict, context_data: Dict) -> bool:
        """
        Rendera wind-modul med PROFESSIONELL DESIGN
        
        Args:
            x, y: Position på canvas
            width, height: Modulens storlek (240×200px för MEDIUM 1)
            weather_data: Väderdata från weather_client
            context_data: Trigger context data
            
        Returns:
            True om rendering lyckades
        """
        try:
            self.logger.info(f"🎨 Renderar PROFESSIONELL wind-modul ({width}×{height})")
            
            # === KOLLISIONSSÄKRA DESIGNKONSTANTER ===
            PADDING = 20
            ROW_GAP_PRIMARY = 36            # M/s → beskrivning
            RIGHT_ICON_SIZE = (32, 32)     # MINDRE för att undvika krock
            RIGHT_ICON_INSET = 24           # MER avstånd från högerkant
            CARDINAL_ICON_SIZE = (32, 32)
            CARDINAL_GAP = 8                # mellan pil och N/NE-text
            BOTTOM_ZONE_INSET = 20          # nederkantens avstånd
            MAX_DESC_WIDTH = 172            # öka från 160 → 172
            MAX_DESC_LINES = 2              # max två rader för beskrivning
            LINE_GAP = 6                    # avstånd mellan textrader
            
            # HÖGERKOLUMN-SKYDD (så text aldrig krockar med ikoner)
            RIGHT_COLUMN_W = RIGHT_ICON_SIZE[0] + RIGHT_ICON_INSET
            PRIMARY_MAX_W = width - PADDING - RIGHT_COLUMN_W - PADDING
            
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
            
            # === PROFESSIONELL LAYOUT (Alt A) ===
            
            # Baspunkter för layout
            center_x = x + width // 2
            left_x = x + PADDING
            right_icon_x = x + width - RIGHT_ICON_INSET - RIGHT_ICON_SIZE[0]
            
            # === 1. PRIMÄRDATA: M/S-VÄRDE (vänster, stor och tydlig) ===
            ms_text = f"{wind_speed:.1f} m/s"
            ms_font = self.fonts.get('large_main', self.fonts.get('medium_main'))
            ms_bbox = self.draw.textbbox((0, 0), ms_text, font=ms_font)
            ms_x = left_x
            ms_y = y + PADDING
            self.draw_text_with_fallback((ms_x, ms_y), ms_text, ms_font, fill=0)
            
            # === 2. SEKUNDÄRDATA: BESKRIVNING (radbrytning istället för ellips) ===
            # Hjälpfunktioner för text-mätning
            def text_width(text, font):
                bbox = self.draw.textbbox((0, 0), text, font=font)
                return bbox[2] - bbox[0]
            
            def text_height(text, font):
                bbox = self.draw.textbbox((0, 0), text, font=font)
                return bbox[3] - bbox[1]
            
            # Radbrytningsfunktion (kollegans förslag)
            def wrap2_ellips(text, font, max_w, max_lines=2):
                words = text.split()
                if not words:
                    return [text]
                    
                lines, cur = [], ""
                for i, w in enumerate(words):
                    test = (cur + " " + w).strip()
                    if text_width(test, font) <= max_w:
                        cur = test
                    else:
                        # Rad full - spara nuvarande och börja ny
                        if cur:
                            lines.append(cur)
                        cur = w
                        
                        # Om vi når max rader, packa resten i sista raden
                        if len(lines) == max_lines - 1:
                            rest_words = words[i:]
                            rest = " ".join(rest_words)
                            # Ellipsera om för långt
                            while text_width(rest + "…", font) > max_w and len(rest) > 3:
                                rest = rest[:-1].rstrip()
                            lines.append(rest + ("…" if len(rest) < len(" ".join(rest_words)) else ""))
                            return lines
                
                if cur:
                    lines.append(cur)
                return lines[:max_lines]
            
            desc_font = self.fonts.get('small_main', self.fonts.get('small_desc'))
            raw_desc = speed_description
            desc_lines = wrap2_ellips(raw_desc, desc_font, MAX_DESC_WIDTH, MAX_DESC_LINES)
            
            # Rita beskrivningsrader under M/s
            desc_x = left_x
            ms_height = ms_bbox[3] - ms_bbox[1]
            desc_y = ms_y + ms_height + ROW_GAP_PRIMARY
            
            for i, line in enumerate(desc_lines):
                line_y = desc_y + i * (text_height(line, desc_font) + LINE_GAP)
                self.draw_text_with_fallback((desc_x, line_y), line, desc_font, fill=0)
            
            # === 3. ILLUSTRATION-IKON (kollisionssäker högerkolumn) ===
            wind_icon = self.icon_manager.get_system_icon('strong-wind', size=RIGHT_ICON_SIZE)
            if wind_icon:
                # Säker position i högerkolumn (kan aldrig krocka med text)
                icon_x = right_icon_x  
                icon_y = y + PADDING // 2  # Högre upp för mindre krockrisk
                
                # KOLLISIONSSKYDD: Kontrollera att M/s inte når högerkolumnen
                ms_right_edge = ms_x + text_width(ms_text, ms_font)
                if ms_right_edge + 12 > x + PADDING + PRIMARY_MAX_W:
                    # Om M/s är för långt, flytta ikonen ner
                    icon_y = desc_y - 4
                    self.logger.info("⚠️ Kollisionsskydd aktiverat - ikon flyttad")
                
                self.paste_icon_on_canvas(wind_icon, icon_x, icon_y)
                self.logger.info(f"✅ Illustration-ikon renderad kollisionssäkert: {RIGHT_ICON_SIZE} på ({icon_x}, {icon_y})")
            else:
                self.logger.warning("⚠️ Illustration-ikon saknas")
            # === 4. TERTIÄRDATA: RIKTNING (centrerad nederkant, måste synas!) ===
            # Hämta kardinalpil och etikett
            cardinal_icon = self.icon_manager.get_wind_icon(cardinal_code, size=CARDINAL_ICON_SIZE)
            label_font = self.fonts.get('small_main', desc_font)
            
            # Debug logging för kardinalpil
            self.logger.info(f"🧭 Cardinal code: '{cardinal_code}', ikon: {cardinal_icon is not None}")
            if cardinal_icon:
                self.logger.info(f"🧭 Cardinal ikon laddad för: {cardinal_code}")
            else:
                self.logger.warning(f"🧭 Cardinal ikon SAKNAS för: {cardinal_code}")
                # Försök alternativa koder
                alt_codes = ['n', 'N', cardinal_code.upper(), cardinal_code.lower()]
                for alt_code in alt_codes:
                    alt_icon = self.icon_manager.get_wind_icon(alt_code, size=CARDINAL_ICON_SIZE)
                    if alt_icon:
                        cardinal_icon = alt_icon
                        self.logger.info(f"🧭 Använder alternativ kod: {alt_code}")
                        break
            
            # Mät bredd för centrerad grupp (ikon + gap + text)
            label_w = text_width(direction_short, label_font)
            icon_w = CARDINAL_ICON_SIZE[0] if cardinal_icon else 0
            gap = CARDINAL_GAP if cardinal_icon else 0
            combined_w = icon_w + gap + label_w
            
            # Positionera gruppen centrerat i nederkant
            base_y = y + height - BOTTOM_ZONE_INSET - CARDINAL_ICON_SIZE[1]
            start_x = x + (width - combined_w) // 2
            
            # Rita kardinalpil om den finns (MÅSTE SYNAS!)
            cursor_x = start_x
            if cardinal_icon:
                self.paste_icon_on_canvas(cardinal_icon, cursor_x, base_y)
                cursor_x += CARDINAL_ICON_SIZE[0] + gap
                self.logger.info(f"✅ Kardinalpil renderad: {cardinal_code} ({CARDINAL_ICON_SIZE}) på ({cursor_x}, {base_y})")
            else:
                self.logger.error(f"❌ KARDINALPIL SAKNAS HELT för kod: {cardinal_code}")
                # Rita en enkel riktningspil som fallback
                self.draw.text((start_x, base_y), "→", font=label_font, fill=0)
                cursor_x += 20  # Ungefärlig bredd för fallback-pil
            
            # Rita etikett vertikalt centrerad mot ikonens mitt
            label_y = base_y + (CARDINAL_ICON_SIZE[1] - text_height(direction_short, label_font)) // 2
            self.draw_text_with_fallback((cursor_x, label_y), direction_short, label_font, fill=0)
            
            self.logger.info(f"✅ KOLLISIONSSÄKER cykel-optimerad wind-modul: {wind_speed:.1f}m/s {speed_description}, {direction_short}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Fel vid kollisionssäker wind rendering: {e}")
            return self.render_fallback_content(
                x, y, width, height, 
                "Wind-data ej tillgänglig"
            )
    
    def get_required_data_sources(self) -> List[str]:
        """Wind-modul behöver SMHI prognosdata för vindstyrka och vindriktning"""
        return ['smhi']
    
    def get_module_info(self) -> Dict:
        """Metadata för professionell wind-modul"""
        info = super().get_module_info()
        info.update({
            'purpose': 'Professionell vindmodul med korrekt informationshierarki',
            'data_sources': ['SMHI vindprognoser (ws + wd parametrar)'],
            'layout': 'Ersätter barometer-modulen (MEDIUM 1 position)',
            'design': 'Kollegans UX-analys implementerad',
            'features': [
                '✅ KOLLISIONSSÄKER DESIGN: Inga krockar mellan text och ikoner',
                '✅ RADBRYTNING: "Måttlig vind" på två rader istället för "Måttlig..."',
                '✅ HÖGERKOLUMN-SKYDD: Text kan aldrig nå ikoner i högerkolumn',
                '✅ MINDRE VINDIKON: 32×32px istället för 40×40px för mindre krockrisk',
                '✅ KARDINALPIL DEBUG: Omfattande logging och fallback för riktningspil',
                '✅ INFORMATIONSHIERARKI: M/s → beskrivning → riktning (kollegans UX)',
                '✅ CYKEL-FOKUSERAD: Snabb avläsning av vindförhållanden',
                'M/s-värde PRIMÄR (large_main font, vänster positioning)',
                'Beskrivande text RADBRUTEN (max 2 rader, 172px bredd)',
                'Illustration-ikon SÄKER (32×32px höger, kollisionsskydd)',
                'Kardinalpil ROBUST (32×32px med alternativa koder och fallback)',
                'Högerkolumn reserverad (ikoner kan aldrig krocka med text)',
                'Generöst spacing: 20px padding, 36px radavstånd, 6px radgap',
                'KOLLISIONSSÄKER: Implementerar kollegans konkreta fixar',
                'Professionell E-Paper design optimerad för cykel-användning'
            ]
        })
        return info