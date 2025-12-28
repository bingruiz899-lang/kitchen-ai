import streamlit as st
from openai import OpenAI
import datetime

# ==========================================
# 1. 配置区域 (保持云端配置不变)
# ==========================================
# 依然从 Secrets 读取密码，安全第一
if "MIMO_API_KEY" in st.secrets:
    API_KEY = st.secrets["MIMO_API_KEY"]
else:
    # 兼容本地运行，如果没有 secrets 则使用空字符串防报错
    API_KEY = "" 

BASE_URL = "https://api.xiaomimimo.com/v1"
MODEL_NAME = "mimo-v2-flash"

# 初始化客户端
if API_KEY:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
else:
    st.error("⚠️ 还没检测到 API Key，请检查 Secrets 设置！")
    st.stop()

# ==========================================
# 2. 核心大厨逻辑
# ==========================================

def get_ai_response(system_role, user_prompt):
    """通用的 AI 调用函数"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 哎呀，网络有点小差错：{str(e)}"

# ==========================================
# 3. 页面美化与设置 (关怀模式)
# ==========================================

st.set_page_config(page_title="爸妈的幸福餐桌", page_icon="🍲", layout="wide")

# 🎨 注入 CSS 样式：把字变大，按钮变大，适合长辈阅读
st.markdown("""
    <style>
    /* 全局字体加大 */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', sans-serif;
    }
    div.stMarkdown p {
        font-size: 1.2rem !important; /* 正文大号字 */
        line-height: 1.8 !important;
    }
    h1 { color: #FF4B4B; }
    h2, h3 { color: #333333; }
    
    /* 按钮样式优化 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-size: 20px !important;
        font-weight: bold;
    }
    
    /* 表格样式 */
    table {
        width: 100%;
        font-size: 1.1rem !important;
    }
    th {
        background-color: #f0f2f6;
        color: #31333F;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. 侧边栏：口味遥控器
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921822.png", width=100)
    st.header("⚙️ 爸妈的口味设置")
    st.markdown("不用打字，点这里调整口味👇")
    
    # 这种选择框比打字方便
    taste_pref = st.selectbox(
        "最近口味偏好：",
        ["清淡养生 (少油盐)", "开胃下饭 (微辣)", "软烂易嚼 (护牙齿)", "强身健体 (高蛋白)"]
    )
    
    cook_time = st.radio(
        "做饭想花多久？",
        ["简单快手 (20分钟)", "精心烹饪 (1小时)", "老火靓汤 (慢炖)"]
    )

# ==========================================
# 5. 主界面内容
# ==========================================

st.title("🏡 爸妈的幸福餐桌")
st.caption("💖 儿子/女儿用 AI 为你们定制的私人小厨房")

# 获取当前时间，送上问候
hour = datetime.datetime.now().hour
greeting = "早安" if hour < 11 else "午安" if hour < 17 else "晚上好"
st.success(f"👴👵 爸妈{greeting}！今天想吃点什么呢？当前设定：**{taste_pref}**")

tab1, tab2, tab3 = st.tabs(["🥘 冰箱有啥 (做菜)", "📅 一周安排 (计划)", "📝 买菜清单 (助手)"])

# --- 功能一：做菜灵感 ---
with tab1:
    st.markdown("### 🥕 冰箱里剩啥菜了？")
    st.markdown("告诉我一两样食材，我来教你们怎么搭配最好吃！")
    
    # 预设一些常见食材标签，点击自动填入（Streamlit原生不支持点击填入，这里用更简单的多选）
    # 但为了简单，还是保留输入框，配上大字体提示
    ingredients = st.text_input("在这里打字，或者语音输入：", placeholder="例如：鸡蛋、豆腐...")
    
    if st.button("🍳 帮我想个做法"):
        if not ingredients:
            st.warning("⚠️ 爸妈，先输入食材哦！")
        else:
            with st.spinner('大厨正在翻菜谱...'):
                prompt = f"""
                我父母想用【{ingredients}】做菜。
                他们的口味偏好是：{taste_pref}。
                时间要求：{cook_time}。
                
                请推荐一道菜，格式要求：
                1. 菜名（好听一点）。
                2. 为什么推荐（结合健康功效）。
                3. 做法（大白话，不要专业术语，分步骤）。
                4. 温馨提示（关于火候或调味）。
                """
                res = get_ai_response("你是一个贴心的家庭厨师长", prompt)
                st.info("👇 推荐做法来啦")
                st.markdown(res)

# --- 功能二：周计划 ---
with tab2:
    st.markdown("### 🗓️ 本周三餐规划")
    st.markdown("点一下按钮，生成一周不重样的健康菜单。")
    
    col_plan_btn, col_copy_btn = st.columns([1,1])
    
    with col_plan_btn:
        generate_btn = st.button("🔄 生成新菜单")
    
    if generate_btn:
        with st.spinner('正在计算营养搭配，请稍等...'):
            prompt = f"""
            请为我的父母制定【本周7天的三餐计划】。
            口味要求：{taste_pref}。
            要求：
            1. 必须输出为 Markdown 表格。
            2. 表格列为：星期、早餐、午餐、晚餐。
            3. 如果一顿饭有多个菜，请用中文顿号（、）分隔，不要使用 <br> 或换行符。
            4. 菜品要家常、易购买。
            5. 表格下方给一段简短的【本周营养重点】。
            """
            plan_res = get_ai_response("你是专业的营养师", prompt)
            
            # ==========================================
            # 🧹 强力清洗代码：这里是专门去 <br> 的
            # ==========================================
            # 无论 AI 听不听话，我们都强制把 <br> 替换成顿号
            plan_res = plan_res.replace("<br>", "、").replace("<br/>", "、")
            
            # 存入 session_state
            st.session_state['week_plan'] = plan_res
            st.rerun() # 刷新页面

    # 显示结果
    if 'week_plan' in st.session_state:
        st.markdown(st.session_state['week_plan'])
        
        # 准备一段方便复制的纯文本
        st.markdown("---")
        st.markdown("📋 **长按下面的文字复制，发到微信群里保存：**")
        st.code(st.session_state['week_plan'], language=None)


# --- 功能三：买菜清单 (新增功能) ---
with tab3:
    st.markdown("### 🛒 照着这个去超市")
    
    if 'week_plan' not in st.session_state:
        st.info("👈 请先去【一周安排】那个页面生成菜单，然后回来这里，我就能列出清单啦！")
    else:
        if st.button("📝 根据菜单生成购物清单"):
            with st.spinner('正在整理清单...'):
                plan_content = st.session_state['week_plan']
                prompt = f"""
                基于这份菜单：
                {plan_content}
                
                请整理一份【购物清单】。
                1. 按分类排列（蔬菜区、肉类区、干货调料区）。
                2. 只列出主要食材，不要列盐糖油这种家里常备的。
                3. 格式简洁，方便手机查看。
                """
                shop_list = get_ai_response("你是精打细算的管家", prompt)
                st.session_state['shop_list'] = shop_list
                st.rerun()

    if 'shop_list' in st.session_state:
        st.markdown(st.session_state['shop_list'])
        st.markdown("📋 **点击右上角复制图标，或者长按复制：**")
        st.code(st.session_state['shop_list'], language=None)


