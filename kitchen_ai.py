import streamlit as st
from openai import OpenAI
import datetime
import os

# ==========================================
# 1. 配置区域 (云端安全版)
# ==========================================

# 必须是从 Secrets 里读取 (不要写死，也不要留空)
API_KEY = st.secrets["MIMO_API_KEY"] 

# 必须是刚才测试成功的地址 (不能是 siliconflow，也不能是 minimax)
BASE_URL = "https://api.xiaomimimo.com/v1" 

# 必须是测试成功的模型名
MODEL_NAME = "mimo-v2-flash"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ==========================================
# 2. 核心功能函数
# ==========================================

def get_ai_response(prompt):
    """发送指令给 Mimo 并获取回复"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                # 修改点：System Prompt 设定角色为“孝顺的孩子”兼“营养师”
                {"role": "system",
                 "content": "你是一个专业的家庭营养师，也是用户孝顺的子女。请为爸爸妈妈规划饮食。回答要充满关怀，格式必须严格遵守要求。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 出错啦：{str(e)}。\n请检查代码里的 API_KEY 是否填对了。"


def save_weekly_plan(plan_text):
    with open("weekly_plan.txt", "w", encoding="utf-8") as f:
        f.write(plan_text)


def load_weekly_plan():
    if os.path.exists("weekly_plan.txt"):
        with open("weekly_plan.txt", "r", encoding="utf-8") as f:
            return f.read()
    return None


# ==========================================
# 3. 界面显示
# ==========================================

st.set_page_config(page_title="爸妈的专属营养师", page_icon="❤️")

# 标题改为更亲切的称呼
st.title("❤️ 爸妈的专属营养师")
st.caption(f"由 Xiaomi {MODEL_NAME} 提供智力支持")

tab1, tab2 = st.tabs(["🥘 冰箱里有啥？(做菜灵感)", "📅 本周吃什么？(三餐表格)"])

# --- 功能一：智能菜谱 (保持不变，微调语气) ---
with tab1:
    st.markdown("### 💡 爸妈，告诉我冰箱里有啥，我教你们做！")

    ingredients = st.text_input("在这里输入食材（比如：豆腐、绞肉、一点韭菜）：", placeholder="点这里输入...")

    if st.button("帮我想个菜谱 ✨", type="primary"):
        if not ingredients:
            st.warning("⚠️ 爸妈，先输入一点食材哦！")
        else:
            with st.spinner('正在翻阅食谱...'):
                prompt = f"""
                爸爸妈妈手里有这些食材：{ingredients}。
                请推荐一道适合老年人吃的家常菜。
                要求：
                1. 语气亲切，称呼“爸爸妈妈”。
                2. 详细列出【准备工作】、【烹饪步骤】(标明火候)。
                3. 最后加一个【儿女的温馨提示】(关于营养或口感)。
                """
                result = get_ai_response(prompt)
                st.markdown(result)

# --- 功能二：周计划 (重大升级：表格+三餐+评分) ---
with tab2:
    st.markdown("### 🗓️ 本周三餐健康规划表")

    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    today_index = datetime.datetime.now().weekday()
    today_str = weekdays[today_index]

    st.info(f"今天是：**{today_str}**，记得按时吃饭哦！")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🔄 生成本周三餐计划表格"):
            with st.spinner('正在计算营养搭配，绘制表格中...'):
                # --- 这里是核心修改：指令非常具体，要求表格格式 ---
                prompt = """
                请为我的爸爸妈妈制定【本周7天的三餐计划】。

                【核心要求】：
                1. 必须覆盖【早餐、午餐、晚餐】。
                2. 必须以【Markdown 表格】的形式输出，方便阅读。
                3. 菜色要软烂易消化，少油少盐，适合老年人，且每天不重样。

                【输出格式要求】：
                第一部分：Markdown表格
                | 星期 | 早餐 (清淡营养) | 午餐 (丰富主食) | 晚餐 (易消化) |
                |---|---|---|---|
                | 星期一 | ... | ... | ... |
                ... (直到星期日)

                第二部分：本周营养分析报告
                1. **营养丰富度评分**：(给出一个0-100的分数)
                2. **营养师点评**：(分析本周蛋白质、维生素摄入情况，指出亮点)
                3. **给爸妈的话**：(一句温馨的叮嘱)
                """

                plan_result = get_ai_response(prompt)
                save_weekly_plan(plan_result)
                st.session_state['weekly_plan'] = plan_result
                st.success("新菜单已生成！")

    # 显示计划内容
    current_plan = load_weekly_plan()

    if current_plan:
        st.divider()
        # 直接使用 markdown 渲染，它会自动把 Markdown 文本变成漂亮的表格
        st.markdown(current_plan)

    else:
        st.warning("👋 还没有计划，点击上面的按钮生成一份吧！")




