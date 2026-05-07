import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import requests

st.set_page_config(page_title="Climate Portal | ERA5 Global", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-header { font-size: 28px; font-weight: 700; color: #1e3a8a; margin-bottom: 5px; font-family: 'Arial', sans-serif;}
    .sub-header { font-size: 16px; color: #64748b; margin-bottom: 30px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px;}
    .desc-box { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; font-size: 14px; color: #334155; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: justify; line-height: 1.6;}
    .desc-title { font-weight: 700; font-size: 16px; margin-bottom: 12px; color: #0f172a; border-bottom: 2px solid #3b82f6; display: block; padding-bottom: 8px;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_geojsons():
    try:
        world = requests.get("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json").json()
    except:
        world = None
        
    uzb = None
    if os.path.exists("data/uzbekistan.geojson"):
        with open("data/uzbekistan.geojson", "r", encoding="utf-8") as f:
            uzb = json.load(f)
            
    return world, uzb

world_geojson, uzb_geojson = load_geojsons()

translations = {
    "O'zbekcha": {
        "main_title": "Mintaqaviy Iqlim O'zgarishi Portali",
        "sub_title": "ERA5 Sun'iy Yo'ldosh Ma'lumotlari va Sun'iy Intellekt (ML) Tahlili Asosida",
        "loc_header": "HUDUDNI TANLASH",
        "loc_label": "Viloyatni tanlang",
        "var_header": "TAHLIL PARAMETRI",
        "var_label": "O'zgaruvchini tanlang",
        "explore_header": "MA'LUMOTLAR BAZASI",
        "download_btn": "Jadvalni yuklab olish (CSV)",
        "tab1": "Tarixiy ma'lumotlar",
        "tab2": "Kelajak bashorati (2050)",
        "tab3": "Orol dengizi fojiasi",
        "map_hist_title": "Tarixiy Iqlim Xaritasi (1950 - 2025)",
        "map_fut_title": "Kelajak Iqlim Xaritasi (2025 - 2050)",
        "map_slider": "Xarita uchun yilni tanlang:",
        "map_radio_temp": " Harorat",
        "map_radio_precip": " Yog'ingarchilik",
        "desc_map_title": "Bu xarita nima haqida?",
        "desc_map_hist": "Bu oddiy xarita emas, balki **Yevropa Ittifoqining Copernicus (ERA5)** sun'iy yo'ldosh dasturi orqali olingan haqiqiy iqlim manzarasi. Xarita butun Markaziy Osiyoni har bir necha kilometrlik mitti kvadratlarga (piksellarga) bo'lib chiqadi. Ranglarning to'qlashishi (masalan qip-qizil) o'sha hududda yil davomida havo qanchalik isiganini, ochiq ranglar esa nisbatan salqin ekanligini ko'rsatadi. Yillarni surish orqali mintaqamizning qanday qilib yildan-yilga qizib borayotganini o'z ko'zingiz bilan ko'rishingiz mumkin.",
        "desc_map_fut": "Bu xaritada siz **Sun'iy Intellekt (Machine Learning)** tomonidan chizilgan 2050-yilgacha bo'lgan kelajak manzarasini ko'rib turibsiz. Algoritm o'tgan 74 yillik tarixni chuqur o'rganib, har bir mitti hudud uchun alohida bashorat tayyorlagan. Yillarni surib, 2050-yilga kelib yashash hududingizda harorat qanchalik xavfli darajaga chiqishi mumkinligini kuzating.",
        "desc_hist_title": "Yillar kesimida iqlim qanday o'zgardi?",
        "desc_hist": "Ushbu chiziqli grafik 1950-yildan bugungi kungacha bo'lgan o'zgarishlarni ko'rsatadi. O'rtadagi **qizil uzuq chiziq** — bu ko'p yillik me'yor (norma). E'tibor bering, so'nggi yillarda ko'k chiziq tez-tez me'yordan tepaga chiqib ketyapti. Bu tasodifiy issiq ob-havo emas, balki iqlimning global miqyosda isib borayotganining aniq ilmiy isbotidir.",
        "desc_dec_title": "O'n yillik (Dekadal) tendensiya",
        "desc_dec": "Ba'zan 1-2 yillik kuchli sovuq kelishi odamlarni 'global isish yo'q ekan' degan xulosaga olib kelishi mumkin. Bu grafik ana shunday adashtiruvchi omillarni yo'qotish uchun ma'lumotlarni **10 yillik bloklarga** birlashtiradi. Agar ustunlar zinapoya kabi muttasil o'sib borsa, demak mintaqada ortga qaytmas isish jarayoni boshlangan.",
        "desc_proj_title": "2050-yilgacha qanday xavf kutmoqda?",
        "desc_proj": "Ushbu grafik Sun'iy intellektning sizning viloyatingiz uchun qilgan xulosasi hisoblanadi. Moviy chiziq tarixni ko'rsatsa, **qizil chiziq 2050-yil sari yo'nalishni** ko'rsatadi. Modellarimiz tabiatning qonuniyatlarini (natural variance) ham inobatga olgan. Agar qizil chiziq tik ko'tarilayotgan bo'lsa, qishloq xo'jaligi va suv zaxiralari uchun tayyorgarlik ko'rish kerakligini bildiradi.",
        "desc_box_title": "Ekstremal (keskin) ob-havo chastotasi",
        "desc_box": "Quti (Boxplot) grafigi tabiatning qanchalik 'injiq' bo'lib borayotganini tahlil qiladi. Ko'k quti tarixni, qizil quti esa kelajakni bildiradi. Qutining tepaga ko'tarilishi o'rtacha iqlim isishini, **qutining uzayishi** esa kutilmagan anomal issiq yoki sovuq kunlar juda tez-tez takrorlanishini anglatadi.",
        "aral_title": "Orol dengizi fojiasi: Sabablar va dinamika",
        "aral_cause_title": "Inqiroz sababi: Suv oqimi va Sho'rlanish",
        "aral_cause": "Grafik Orol dengiziga quyiladigan asosiy qon tomirlari — Amudaryo va Sirdaryo suv hajmining keskin kamayishi (moviy chiziq) va buning oqibatida dengiz suvining sho'rlanish darajasi (qizil chiziq) qanday halokatli darajada oshib ketganini ko'rsatadi. Suv kelmay qo'ygach, tuz konsentratsiyasi butunlay hayot uchun yaroqsiz holatga kelgan.",
        "aral_effect_title": "Fojia oqibati: Suv sathi va Maydon",
        "aral_effect": "Suv kelishining to'xtashi natijasida dengiz sathi pasayib (to'q ko'k chiziq), uning umumiy maydoni (och moviy ustunlar) yillar davomida qanday tezlikda qurib, cho'lga aylanib ketganligini yaqqol ko'rishingiz mumkin.",
        "aral_micro_title": "Orol fojiasining viloyatlarga mikro-iqlimiy ta'siri",
        "aral_concl_title": "Yopiq zanjir fojiasi (Feedback Loop)",
        "aral_concl": "Bu yerda **Ikki karra inqiroz** yuz berganini ko'rishimiz mumkin: Global isish sababli hududda harorat ko'tariladi -> bu daryo va ko'llardagi suvning tez bug'lanishiga olib keladi -> natijada ulkan suv havzasi o'zining hududni 'sovutib turish' xususiyatini yo'qotadi -> bu esa o'z navbatida mintaqa iqlimining yanada keskin isib ketishiga sabab bo'ladi.",
        "aral_note": "Muhim eslatma: Orol dengizining qurishi asosan unga yaqin hududlarga (Orolbo'yi) to'g'ridan-to'g'ri ta'sir qiladi. Korellyatsiyani aniq ko'rish uchun chap paneldan Qaraqalpogiston yoki Xorazm viloyatini tanlang."
    },
    "English": {
        "main_title": "Regional Climate Change Portal",
        "sub_title": "Powered by ERA5 Satellite Data & Machine Learning",
        "loc_header": "SELECT LOCATION",
        "loc_label": "Choose a Region",
        "var_header": "ANALYSIS PARAMETER",
        "var_label": "Choose a Variable",
        "explore_header": "DATASET",
        "download_btn": "Download Data (CSV)",
        "tab1": "Historical Data",
        "tab2": "Future Projections (2050)",
        "tab3": "Aral Sea Disaster",
        "map_hist_title": "Historical Climate Map (1950 - 2025)",
        "map_fut_title": "Future Climate Projections (2025 - 2050)",
        "map_slider": "Select year:",
        "map_radio_temp": " Temperature",
        "map_radio_precip": " Precipitation",
        "desc_map_title": "Understanding this map",
        "desc_map_hist": "This is a **true Gridded Heatmap** generated from the EU's Copernicus (ERA5) satellite data. The region is divided into thousands of tiny pixels. Darker red areas indicate intense heat accumulation over the year, while lighter areas show cooler zones. By moving the slider, you can visually trace how the warming phenomenon has spread across Central Asia over the decades.",
        "desc_map_fut": "This map reveals the future up to 2050, generated by **Machine Learning algorithms**. The model analyzed 74 years of historical data to independently forecast the climate for each specific grid pixel. Drag the slider to see how temperatures in your specific area might reach critical levels in the coming decades.",
        "desc_hist_title": "Year-by-Year Climate Shifts",
        "desc_hist": "This line chart visualizes annual fluctuations since 1950. The **red dashed line** represents the long-term historical baseline. Notice how the blue line consistently stays above the red line in recent years. This is not just random weather; it is statistical proof of ongoing global warming.",
        "desc_dec_title": "The Decadal Trend",
        "desc_dec": "Short-term weather events can hide the bigger picture. This chart groups data into **10-year blocks (decades)** to filter out that noise. If the bars resemble a continually rising staircase, it confirms a fundamental and irreversible shift in the region's climate.",
        "desc_proj_title": "What awaits us by 2050?",
        "desc_proj": "This is the AI projection for your selected region. While the blue line represents historical data, the **red dashed line shows the trajectory towards 2050**. The model incorporates natural variance. A steep upward trend indicates a severe need for adaptation strategies in agriculture and water management.",
        "desc_box_title": "Volatility and Extreme Weather",
        "desc_box": "The Boxplot analyzes weather extremes rather than just averages. The blue box is the historical baseline, and the red box is the future. A box shifting upward means hotter averages, but a **taller box** means increased weather volatility—meaning unexpected heatwaves or sudden freezes will become much more common.",
        "aral_title": "The Aral Sea Desiccation: Causes & Dynamics",
        "aral_cause_title": "The Cause: Inflow vs Salinity",
        "aral_cause": "This chart illustrates the dramatic decrease in the volume of water flowing into the Aral Sea from its main river arteries (blue line) and the devastating consequence: a lethal spike in water salinity levels (red line) that destroyed the sea's ecosystem.",
        "aral_effect_title": "The Effect: Water Level & Surface Area",
        "aral_effect": "As the water inflow stopped, the sea level plummeted (dark blue line). You can clearly see how rapidly the overall surface area of the sea (light blue bars) shrank over the years, turning a massive body of water into a desert.",
        "aral_micro_title": "Micro-Climatic Impacts on Regions",
        "aral_concl_title": "The Deadly Feedback Loop",
        "aral_concl": "This illustrates a **Dual Crisis**: Regional temperature rises cause accelerated evaporation of water bodies -> leading to the loss of the sea's natural 'cooling effect' -> which in turn causes the climate to become even hotter and drier, creating a vicious cycle.",
        "aral_note": "Scientific Note: The desiccation primarily affects immediately adjacent areas. To view direct statistical correlations, please select Karakalpakstan or Khorezm from the sidebar."
    },
    "Русский": {
        "main_title": "Региональный Климатический Портал",
        "sub_title": "На базе спутниковых данных ERA5 и Машинного Обучения",
        "loc_header": "ВЫБОР РЕГИОНА",
        "loc_label": "Выберите регион",
        "var_header": "ПАРАМЕТР АНАЛИЗА",
        "var_label": "Выберите переменную",
        "explore_header": "БАЗА ДАННЫХ",
        "download_btn": "Скачать таблицу (CSV)",
        "tab1": "Исторические данные",
        "tab2": "Прогнозы будущего (2050)",
        "tab3": "Трагедия Аральского моря",
        "map_hist_title": "Историческая климатическая карта (1950 - 2025)",
        "map_fut_title": "Прогнозная карта (2025 - 2050)",
        "map_slider": "Выберите год:",
        "map_radio_temp": " Температура",
        "map_radio_precip": " Осадки",
        "desc_map_title": "О чем эта карта?",
        "desc_map_hist": "Это **настоящая сплошная тепловая карта (Gridded Heatmap)**, созданная на основе спутниковых данных ЕС Copernicus (ERA5). Регион разделен на тысячи мельчайших пикселей. Темно-красные области указывают на сильное накопление тепла. Перемещая ползунок, вы можете визуально проследить, как волны тепла распространялись по Центральной Азии.",
        "desc_map_fut": "Эта карта показывает будущее до 2050 года, рассчитанное **алгоритмами Машинного Обучения (ML)**. Модель изучила 74-летнюю историю для создания индивидуального прогноза для каждого пикселя. Перемещайте ползунок, чтобы увидеть потенциальные климатические риски для вашей местности.",
        "desc_hist_title": "Ежегодные климатические изменения",
        "desc_hist": "Этот график показывает ежегодные колебания с 1950 года. **Красная пунктирная линия** обозначает многолетнюю норму. Обратите внимание, как в последние годы синяя линия всё чаще оказывается выше нормы. Это не случайность, а статистическое доказательство глобального потепления.",
        "desc_dec_title": "Декадный (10-летний) тренд",
        "desc_dec": "Краткосрочные погодные явления могут скрыть общую картину. Этот график объединяет данные в **10-летние блоки**, чтобы сгладить аномалии. Если столбцы растут как лестница, это подтверждает начало необратимых климатических изменений в регионе.",
        "desc_proj_title": "Что нас ждет к 2050 году?",
        "desc_proj": "Это прогноз ИИ для выбранной области. Синяя линия — история, а **красная пунктирная линия — траектория до 2050 года**. Модель учитывает естественную дисперсию. Резкий рост красной линии сигнализирует о необходимости подготовки сельского хозяйства к новым условиям.",
        "desc_box_title": "Экстремальные погодные явления",
        "desc_box": "График (Boxplot) анализирует экстремальные значения. Синий ящик — прошлое, красный — будущее. Смещение ящика вверх означает потепление, а **увеличение его длины** означает высокую нестабильность погоды (частые аномальные волны тепла или заморозки).",
        "aral_title": "Высыхание Аральского моря: причины и динамика",
        "aral_cause_title": "Причина: Приток воды и Соленость",
        "aral_cause": "График показывает резкое снижение объема воды, поступающей в Аральское море из главных рек (синяя линия), и разрушительное последствие: смертельный скачок уровня солености воды (красная линия), уничтоживший экосистему.",
        "aral_effect_title": "Последствия: Уровень воды и Площадь",
        "aral_effect": "Из-за прекращения притока уровень моря стремительно упал (темно-синяя линия). Вы можете ясно видеть, как быстро общая площадь моря (голубые столбцы) сокращалась с годами, превращаясь в пустыню.",
        "aral_micro_title": "Микроклиматическое воздействие на регионы",
        "aral_concl_title": "Смертельная петля обратной связи",
        "aral_concl": "Здесь наблюдается **Двойной кризис**: Рост температуры ускоряет испарение водоемов -> это приводит к потере морем своей 'охлаждающей' функции -> что, в свою очередь, делает климат еще более жарким и сухим.",
        "aral_note": "Примечание: Высыхание в первую очередь влияет на прилегающие территории. Для просмотра прямой корреляции выберите Каракалпакстан или Хорезм в левой панели."
    }
}

col_empty, col_lang = st.columns([8.8, 1.2])
with col_lang:
    selected_lang = st.selectbox("Til", ["O'zbekcha", "English", "Русский"], label_visibility="collapsed")
    
t = translations[selected_lang]

try:
    col_logo, col_text = st.sidebar.columns([1.2, 4])
    with col_logo:
        st.image("logo.png", use_container_width=True) 
    with col_text:
        st.markdown(
            """
            <div style='color: #1e3a8a; margin-top: 5px; font-weight: 800; font-size: 19px; line-height: 1.2;'>
                Climate Change<br>Portal
            </div>
            """, 
            unsafe_allow_html=True
        )
except Exception:
    st.sidebar.markdown("<h2 style='text-align: center; color: #1e3a8a; margin-top: -20px;'>🌍 Climate Portal</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.markdown(f'<div class="main-header">{t["main_title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">{t["sub_title"]}</div>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/regions_master.csv")
    aral_df = pd.read_csv("data/processed/aral_sea_master.csv")
    
    era5_df, future_era5_df = None, None
    try:
        era5_df = pd.read_csv("data/processed/era5_grid_data.csv")
    except Exception:
        pass
        
    try:
        future_era5_df = pd.read_csv("data/processed/future_era5_grid.csv")
    except Exception:
        pass
    
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    aral_df = aral_df.loc[:, ~aral_df.columns.str.contains('^Unnamed')]
    aral_df.columns = aral_df.columns.str.strip()
    
    df['Decade'] = (df['Year'] // 10) * 10
    df['Decade_Str'] = df['Decade'].astype(str) + "s"
    
    return df, aral_df, era5_df, future_era5_df

df, aral_df, era5_df, future_era5_df = load_data()

st.sidebar.markdown(f"### {t['loc_header']}")
location = st.sidebar.selectbox(t['loc_label'], sorted(df['Viloyat'].dropna().unique()))

st.sidebar.markdown(f"### {t['var_header']}")
variables = [col for col in df.columns if col not in ['Year', 'Viloyat', 'Category', 'Decade', 'Decade_Str']]
parameter = st.sidebar.selectbox(t['var_label'], variables)

df_filtered = df[df['Viloyat'] == location]

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t['explore_header']}")
st.sidebar.download_button(label=t["download_btn"], data=convert_df_to_csv(df_filtered), file_name=f"{location}_climate_data.csv", mime="text/csv")

st.sidebar.markdown("""
    <div style="margin-top: 60px; text-align: center; padding-top: 20px; border-top: 1px solid #e2e8f0;">
        <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #64748b;">Developed by</span><br>
        <strong style="color: #1e3a8a; font-size: 15px;">Jasurbek Begmatov</strong><br>
        <span style="font-size: 12px; color: #64748b;">Software Engineering, TUIT</span>
    </div>
""", unsafe_allow_html=True)

def create_grid_map(df_map, map_var):
    color_scale = px.colors.sequential.Blues if map_var == 'Precipitation' else px.colors.sequential.YlOrRd
    
    fig = px.scatter_mapbox(
        df_map, lat="Lat", lon="Lon", color=map_var, 
        opacity=0.45, color_continuous_scale=color_scale,
        zoom=4.8, center={"lat": 41.37, "lon": 64.58}, 
        mapbox_style="carto-positron",
        hover_data={"Lat": ':.2f', "Lon": ':.2f', map_var: ':.2f'}
    )
    fig.update_traces(marker=dict(size=16))
    
    labels_data = {
        "Qoraqalpog'iston": (43.5, 59.0), "Xorazm": (41.5, 60.5),
        "Navoiy": (41.5, 64.5), "Buxoro": (39.7, 63.5),
        "Samarqand": (39.6, 66.2), "Qashqadaryo": (38.8, 65.8),
        "Surxondaryo": (38.0, 67.5), "Jizzax": (40.2, 67.8),
        "Sirdaryo": (40.5, 68.8), "Toshkent": (41.3, 69.8),
        "Namangan": (41.0, 71.2), "Farg'ona": (40.4, 71.7),
        "Andijon": (40.8, 72.3)
    }
    
    fig.add_trace(go.Scattermapbox(
        lat=[coords[0] for coords in labels_data.values()],
        lon=[coords[1] for coords in labels_data.values()],
        mode="markers",
        marker=dict(size=12, color="#ffffff", opacity=0.9),
        text=list(labels_data.keys()),
        # Oq nuqtaga oborganda faqat Viloyat nomi aniq chiqadi
        hovertemplate="<b>📍 %{text}</b><extra></extra>",
        showlegend=False
    ))

    layers = []
    if world_geojson:
        layers.append(dict(sourcetype='geojson', source=world_geojson, type='line', color='rgba(0,0,0,0.5)', line=dict(width=1)))
    if uzb_geojson:
        layers.append(dict(sourcetype='geojson', source=uzb_geojson, type='line', color='black', line=dict(width=2)))
        
    fig.update_layout(mapbox=dict(layers=layers), margin={"r":0,"t":0,"l":0,"b":0}, height=450)
    return fig

tab_hist, tab_future, tab_aral = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

with tab_hist:
    st.markdown(f"####  {t['map_hist_title']}")
    map_var_choice = st.radio("Map Param Hist", options=[t['map_radio_temp'], t['map_radio_precip']], horizontal=True, label_visibility="collapsed", key="hist_radio")
    map_var = 'Temperature' if map_var_choice == t['map_radio_temp'] else 'Precipitation'
        
    col_m1, col_m2 = st.columns([7, 3])
    with col_m1:
        if era5_df is not None:
            min_year, max_year = int(era5_df['Year'].min()), int(era5_df['Year'].max())
            selected_year = st.slider(t['map_slider'], min_year, max_year, max_year, key="hist_slider")
            df_year_map = era5_df[era5_df['Year'] == selected_year]
            fig_map1 = create_grid_map(df_year_map, map_var)
            st.plotly_chart(fig_map1, width="stretch")
            
    with col_m2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="desc-box"><div class="desc-title">{t['desc_map_title']}</div>{t['desc_map_hist']}</div>""", unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    col1, col2 = st.columns([7, 3])
    with col1:
        fig1 = px.line(df_filtered, x='Year', y=parameter, markers=True, line_shape='spline')
        fig1.update_traces(line_color="#2563eb", marker=dict(size=5))
        fig1.add_hline(y=df_filtered[parameter].mean(), line_dash="dash", line_color="#ef4444", annotation_text="Mean")
        fig1.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=350)
        st.plotly_chart(fig1, width="stretch")
    with col2:
        st.markdown(f"""<div class="desc-box"><div class="desc-title">{t['desc_hist_title']}</div>{t['desc_hist']}</div>""", unsafe_allow_html=True)

    col3, col4 = st.columns([7, 3])
    with col3:
        decadal_df = df_filtered.groupby('Decade_Str')[parameter].mean().reset_index()
        fig2 = px.bar(decadal_df, x='Decade_Str', y=parameter, text_auto='.2f')
        fig2.update_traces(marker_color="#0ea5e9")
        fig2.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=350)
        st.plotly_chart(fig2, width="stretch")
    with col4:
        st.markdown(f"""<div class="desc-box"><div class="desc-title">{t['desc_dec_title']}</div>{t['desc_dec']}</div>""", unsafe_allow_html=True)

with tab_future:
    st.markdown(f"#### 🗺️ {t['map_fut_title']}")
    map_var_choice_fut = st.radio("Map Param Fut", options=[t['map_radio_temp'], t['map_radio_precip']], horizontal=True, label_visibility="collapsed", key="fut_radio")
    map_var_fut = 'Temperature' if map_var_choice_fut == t['map_radio_temp'] else 'Precipitation'
    
    col_mf1, col_mf2 = st.columns([7, 3])
    with col_mf1:
        if future_era5_df is not None:
            min_f_year, max_f_year = int(future_era5_df['Year'].min()), int(future_era5_df['Year'].max())
            selected_f_year = st.slider(t['map_slider'], min_f_year, max_f_year, max_f_year, key="fut_slider")
            df_fut_year_map = future_era5_df[future_era5_df['Year'] == selected_f_year]
            fig_map_fut = create_grid_map(df_fut_year_map, map_var_fut)
            st.plotly_chart(fig_map_fut, width="stretch")
        else:
            st.info("Jupyter Notebook'dagi ML kodni ishlatganingizdan so'ng, bu yerda kelajak xaritasi paydo bo'ladi.")
            
    with col_mf2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""<div class="desc-box"><div class="desc-title">{t['desc_map_title']}</div>{t['desc_map_fut']}</div>""", unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    try:
        future_df = pd.read_csv("data/processed/future_predictions.csv")
        col_f1, col_f2 = st.columns([7, 3])
        x_hist, y_hist = df_filtered['Year'].values, df_filtered[parameter].values
        y_future = []
        
        with col_f1:
            future_filtered = future_df[(future_df['Viloyat'] == location) & (future_df['Parameter'] == parameter)]
            x_future, y_future = future_filtered['Year'].values, future_filtered['Predicted_Value'].values
            
            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(x=x_hist, y=y_hist, mode='lines', name='Historical', line=dict(color='#3b82f6', width=2)))
            if len(x_future) > 0:
                fig_proj.add_trace(go.Scatter(x=[x_hist[-1], x_future[0]], y=[y_hist[-1], y_future[0]], mode='lines', showlegend=False, line=dict(color='#ef4444', dash='dash', width=2)))
                fig_proj.add_trace(go.Scatter(x=x_future, y=y_future, mode='lines', name='ML Projection (2050)', line=dict(color='#ef4444', dash='dash', width=2)))
            fig_proj.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=400)
            st.plotly_chart(fig_proj, width="stretch")
        with col_f2:
            st.markdown(f"""<div class="desc-box"><div class="desc-title">{t['desc_proj_title']}</div>{t['desc_proj']}</div>""", unsafe_allow_html=True)

        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        if len(y_future) > 0:
            col_f3, col_f4 = st.columns([7, 3])
            with col_f3:
                hist_box = pd.DataFrame({'Value': y_hist, 'Period': 'Historical'})
                fut_box = pd.DataFrame({'Value': y_future, 'Period': 'Projection'})
                box_df = pd.concat([hist_box, fut_box])
                
                fig_box = px.box(box_df, x='Period', y='Value', color='Period', 
                                 color_discrete_map={'Historical': '#3b82f6', 'Projection': '#ef4444'}, points="all")
                fig_box.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=400, xaxis_title="", yaxis_title=parameter)
                st.plotly_chart(fig_box, width="stretch")
            with col_f4:
                st.markdown(f"""<div class="desc-box"><div class="desc-title">{t['desc_box_title']}</div>{t['desc_box']}</div>""", unsafe_allow_html=True)
                
    except Exception:
        pass

with tab_aral:
    st.markdown(f"### {t['tab3']}")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        fig_cause = make_subplots(specs=[[{"secondary_y": True}]])
        total_river = aral_df['Amudaryo volume'] + aral_df['Sirdaryo volume']
        salinity_col = [col for col in aral_df.columns if 'Salinity' in col][-1] 
        fig_cause.add_trace(go.Scatter(x=aral_df['Year'], y=total_river, name="Inflow (Amu+Sir)", line=dict(color='#3b82f6')), secondary_y=False)
        fig_cause.add_trace(go.Scatter(x=aral_df['Year'], y=aral_df[salinity_col], name="Salinity", line=dict(color='#ef4444')), secondary_y=True)
        fig_cause.update_layout(template="plotly_white", margin=dict(t=40, b=0, l=0, r=0), height=350)
        st.plotly_chart(fig_cause, width="stretch")
        st.markdown(f"""<div class="desc-box"><div class="desc-title">{t['aral_cause_title']}</div>{t['aral_cause']}</div>""", unsafe_allow_html=True)

    with col_a2:
        fig_effect = make_subplots(specs=[[{"secondary_y": True}]])
        area_col = [col for col in aral_df.columns if 'area' in col.lower()][0]
        level_col = [col for col in aral_df.columns if 'level' in col.lower()][0]
        fig_effect.add_trace(go.Bar(x=aral_df['Year'], y=aral_df[area_col], name="Surface Area", marker_color='#93c5fd'), secondary_y=False)
        fig_effect.add_trace(go.Scatter(x=aral_df['Year'], y=aral_df[level_col], name="Water Level", line=dict(color='#1e3a8a', width=3)), secondary_y=True)
        fig_effect.update_layout(template="plotly_white", margin=dict(t=40, b=0, l=0, r=0), height=350)
        st.plotly_chart(fig_effect, width="stretch")
        st.markdown(f"""<div class="desc-box"><div class="desc-title">{t['aral_effect_title']}</div>{t['aral_effect']}</div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"### {t['aral_micro_title']}")
    
    aral_regions = ['qaraqal', 'qoraqal', 'karakal', 'xoraz', 'khore']
    if any(reg in location.lower() for reg in aral_regions):
        col_a3, col_a4 = st.columns(2)
        with col_a3:
            merged_area = pd.merge(df_filtered[['Year', parameter]], aral_df[['Year', area_col]], on='Year', how='inner')
            fig_corr = make_subplots(specs=[[{"secondary_y": True}]])
            fig_corr.add_trace(go.Scatter(x=merged_area['Year'], y=merged_area[area_col], name="Aral Area", fill='tozeroy', line=dict(color='#bfdbfe', width=1)), secondary_y=False)
            fig_corr.add_trace(go.Scatter(x=merged_area['Year'], y=merged_area[parameter], name=f"Variable", line=dict(color='#ef4444', width=2)), secondary_y=True)
            fig_corr.update_layout(template="plotly_white", margin=dict(t=40, b=0, l=0, r=0), height=380)
            st.plotly_chart(fig_corr, width="stretch")

        with col_a4:
            try:
                evap_col = [col for col in aral_df.columns if 'evapor' in col.lower()][0]
                temp_cols = [col for col in df_filtered.columns if 'temperature' in col.lower() and 'mean' in col.lower()]
                temp_col = temp_cols[0] if temp_cols else [col for col in df_filtered.columns if 'temperature' in col.lower()][0]
                merged_evap = pd.merge(df_filtered[['Year', temp_col]], aral_df[['Year', evap_col]], on='Year', how='inner')
                fig_evap = make_subplots(specs=[[{"secondary_y": True}]])
                fig_evap.add_trace(go.Bar(x=merged_evap['Year'], y=merged_evap[evap_col], name="Evaporation", marker_color='#fdba74'), secondary_y=False)
                fig_evap.add_trace(go.Scatter(x=merged_evap['Year'], y=merged_evap[temp_col], name="Mean Temp", line=dict(color='#b91c1c', width=3)), secondary_y=True)
                fig_evap.update_layout(template="plotly_white", margin=dict(t=40, b=0, l=0, r=0), height=380)
                st.plotly_chart(fig_evap, width="stretch")
            except Exception:
                pass
                
        st.markdown(f"""<br><div class="desc-box"><div class="desc-title">{t['aral_concl_title']}</div>{t['aral_concl']}</div>""", unsafe_allow_html=True)
    else:
        st.info(t['aral_note'])