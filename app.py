import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_manager import DataManager
from utils import *
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="LeetCode DSA Mastery",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        border-radius: 5px;
        height: 3em;
        font-weight: 500;
    }
    .problem-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    div[data-testid="stExpander"] {
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
        background: #e3f2fd;
        color: #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Data Manager
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Initialize Session State
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'Learning Path'

def main():
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("💻 LeetCode DSA Mastery")
        st.markdown("*Your journey from Beginner to Expert*")
    
    with col2:
        stats = data_manager.get_progress_stats()
        st.metric("Solved", f"{stats['solved_count']}/{stats['total_problems']}")
    
    with col3:
        st.metric("Progress", f"{stats['completion_percentage']:.1f}%")
    
    # Sidebar
    render_sidebar()
    
    # Main Content based on view mode
    view_mode = st.session_state.view_mode
    
    if view_mode == "🎯 Learning Path":
        show_learning_path_view()
    elif view_mode == "📋 All Problems":
        show_all_problems_view()
    elif view_mode == "📂 By Topic":
        show_by_topic_view()
    elif view_mode == "🔖 Bookmarked":
        show_bookmarked_view()
    elif view_mode == "📊 Analytics":
        show_analytics_view()
    elif view_mode == "💡 Recommendations":
        show_recommendations_view()

def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/code.png", width=80)
        st.markdown("## Navigation")
        
        # View Mode Selection
        view_modes = [
            "🎯 Learning Path",
            "📋 All Problems",
            "📂 By Topic",
            "🔖 Bookmarked",
            "💡 Recommendations",
            "📊 Analytics"
        ]
        
        selected_view = st.radio("View", view_modes, key='view_selector')
        st.session_state.view_mode = selected_view
        
        st.markdown("---")
        
        # Progress Overview
        st.markdown("### 📈 Quick Stats")
        stats = data_manager.get_progress_stats()
        
        # Progress bar
        st.progress(stats['completion_percentage'] / 100)
        st.caption(f"{stats['solved_count']} of {stats['total_problems']} problems solved")
        
        # Difficulty breakdown
        st.markdown("#### By Difficulty")
        diff_stats = stats['difficulty_stats']
        total_by_diff = {
            'Easy': len(data_manager.get_problems_by_difficulty('Easy')),
            'Medium': len(data_manager.get_problems_by_difficulty('Medium')),
            'Hard': len(data_manager.get_problems_by_difficulty('Hard'))
        }
        
        for diff in ['Easy', 'Medium', 'Hard']:
            emoji = get_difficulty_emoji(diff)
            solved = diff_stats.get(diff, 0)
            total = total_by_diff[diff]
            st.metric(f"{emoji} {diff}", f"{solved}/{total}")
        
        st.markdown("---")
        
        # Filters (show only in relevant views)
        if selected_view in ["📋 All Problems", "📂 By Topic"]:
            st.markdown("### 🔍 Filters")
            
            # Difficulty Filter
            difficulties = st.multiselect(
                "Difficulty",
                ['Easy', 'Medium', 'Hard'],
                default=['Easy', 'Medium', 'Hard'],
                key='difficulty_filter'
            )
            
            # Topic Filter
            topics = st.multiselect(
                "Topics",
                data_manager.get_topics(),
                default=data_manager.get_topics(),
                key='topic_filter'
            )
            
            # Pattern Filter
            patterns = st.multiselect(
                "Patterns",
                data_manager.get_patterns(),
                key='pattern_filter'
            )
            
            # Status Filter
            col1, col2 = st.columns(2)
            with col1:
                show_solved = st.checkbox("Solved", value=True, key='show_solved')
            with col2:
                show_unsolved = st.checkbox("Unsolved", value=True, key='show_unsolved')
            
            st.session_state.filters = {
                'difficulties': difficulties,
                'topics': topics,
                'patterns': patterns,
                'show_solved': show_solved,
                'show_unsolved': show_unsolved,
                'solved_ids': data_manager.progress['solved_problems']
            }
        
        st.markdown("---")
        
        # Export Options
        if st.button("📥 Export Progress"):
            csv = export_progress_to_csv(data_manager)
            st.download_button(
                "Download CSV",
                csv,
                "leetcode_progress.csv",
                "text/csv"
            )

def show_learning_path_view():
    st.header("🎯 Structured Learning Path")
    st.markdown("Follow this curated path to master DSA systematically")
    
    learning_paths = data_manager.get_all_learning_paths()
    solved_ids = set(data_manager.progress['solved_problems'])
    
    for path_key, path_data in learning_paths.items():
        problem_ids = path_data['problem_ids']
        problems = [data_manager.get_problem_by_id(pid) for pid in problem_ids]
        problems = [p for p in problems if p is not None]
        
        solved_in_path = len(set(problem_ids) & solved_ids)
        total_in_path = len(problem_ids)
        completion = (solved_in_path / total_in_path * 100) if total_in_path > 0 else 0
        
        with st.expander(f"📚 {path_data['name']} - {solved_in_path}/{total_in_path} completed", expanded=(completion < 100)):
            st.markdown(f"*{path_data['description']}*")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.progress(completion / 100)
            with col2:
                st.markdown(f"**{completion:.0f}%**")
            
            st.markdown("---")
            
            for problem in problems:
                render_problem_card(problem, data_manager)

def show_all_problems_view():
    st.header("📋 All Problems")
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔎 Search problems", "", key='search_input')
    with col2:
        sort_by = st.selectbox("Sort by", ["ID", "Difficulty", "Title"], key='sort_by')
    
    # Get problems
    if search_query:
        problems = data_manager.search_problems(search_query)
    else:
        problems = data_manager.get_all_problems()
    
    # Apply filters
    if 'filters' in st.session_state:
        problems = filter_problems(problems, st.session_state.filters)
    
    # Sort
    if sort_by == "ID":
        problems.sort(key=lambda x: x['id'])
    elif sort_by == "Difficulty":
        diff_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        problems.sort(key=lambda x: diff_order[x['difficulty']])
    else:
        problems.sort(key=lambda x: x['title'])
    
    st.markdown(f"**Showing {len(problems)} problems**")
    
    for problem in problems:
        render_problem_card(problem, data_manager)

def show_by_topic_view():
    st.header("📂 Problems by Topic")
    
    # Get all problems
    all_problems = data_manager.get_all_problems()
    
    # Apply filters
    if 'filters' in st.session_state:
        all_problems = filter_problems(all_problems, st.session_state.filters)
    
    # Group by topic
    topics = {}
    for problem in all_problems:
        topic = problem['topic']
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(problem)
    
    # Display by topic
    solved_ids = set(data_manager.progress['solved_problems'])
    
    for topic in sorted(topics.keys()):
        topic_problems = topics[topic]
        solved_in_topic = len([p for p in topic_problems if p['id'] in solved_ids])
        total_in_topic = len(topic_problems)
        
        with st.expander(f"**{topic}** - {solved_in_topic}/{total_in_topic} solved", expanded=False):
            for problem in topic_problems:
                render_problem_card(problem, data_manager, compact=True)

def show_bookmarked_view():
    st.header("🔖 Bookmarked Problems")
    
    bookmarked_ids = data_manager.progress['bookmarked_problems']
    
    if not bookmarked_ids:
        st.info("📌 No bookmarked problems yet. Bookmark important problems to review them later!")
        return
    
    problems = [data_manager.get_problem_by_id(pid) for pid in bookmarked_ids]
    problems = [p for p in problems if p is not None]
    
    st.markdown(f"**{len(problems)} bookmarked problems**")
    
    for problem in problems:
        render_problem_card(problem, data_manager)

def show_recommendations_view():
    st.header("💡 Recommended for You")
    st.markdown("Based on your progress and learning path")
    
    recommended = get_recommended_problems(data_manager, data_manager.progress, limit=10)
    
    if not recommended:
        st.success("🎉 Congratulations! You've solved all high-priority problems!")
        return
    
    st.markdown(f"**Top {len(recommended)} problems to solve next:**")
    
    for i, problem in enumerate(recommended, 1):
        st.markdown(f"### {i}. Recommended")
        render_problem_card(problem, data_manager)
        st.markdown("---")

def show_analytics_view():
    st.header("📊 Analytics Dashboard")
    
    stats = data_manager.get_progress_stats()
    
    # Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(style_metric_card(
            "Total Solved",
            str(stats['solved_count']),
            f"+{stats['solved_count']}"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(style_metric_card(
            "Completion",
            f"{stats['completion_percentage']:.1f}%"
        ), unsafe_allow_html=True)
    
    with col3:
        streak = calculate_streak(data_manager.progress.get('solve_history', []))
        st.markdown(style_metric_card(
            "Current Streak",
            f"{streak} days",
            "🔥"
        ), unsafe_allow_html=True)
    
    with col4:
        time_spent = format_time(stats['total_time_spent'])
        st.markdown(style_metric_card(
            "Time Spent",
            time_spent
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Difficulty Distribution
        st.subheader("📊 By Difficulty")
        diff_data = pd.DataFrame({
            'Difficulty': ['Easy', 'Medium', 'Hard'],
            'Solved': [
                stats['difficulty_stats'].get('Easy', 0),
                stats['difficulty_stats'].get('Medium', 0),
                stats['difficulty_stats'].get('Hard', 0)
            ]
        })
        
        fig = px.pie(
            diff_data,
            values='Solved',
            names='Difficulty',
            color='Difficulty',
            color_discrete_map={
                'Easy': '#00b8a9',
                'Medium': '#f8b500',
                'Hard': '#e63946'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Topic Distribution
        st.subheader("📂 By Topic")
        topic_stats = stats['topic_stats']
        
        if topic_stats:
            topic_data = pd.DataFrame({
                'Topic': list(topic_stats.keys()),
                'Solved': list(topic_stats.values())
            }).sort_values('Solved', ascending=False).head(10)
            
            fig = px.bar(
                topic_data,
                x='Solved',
                y='Topic',
                orientation='h',
                color='Solved',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start solving problems to see topic distribution")
    
    # Progress Over Time
    st.subheader("📈 Progress Over Time")
    solve_history = data_manager.progress.get('solve_history', [])
    
    if solve_history:
        history_df = pd.DataFrame(solve_history)
        history_df['date'] = pd.to_datetime(history_df['timestamp']).dt.date
        daily_solves = history_df.groupby('date').size().reset_index(name='count')
        daily_solves['cumulative'] = daily_solves['count'].cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_solves['date'],
            y=daily_solves['cumulative'],
            mode='lines+markers',
            name='Cumulative Problems',
            line=dict(color='#667eea', width=3),
            fill='tozeroy'
        ))
        fig.update_layout(
            title="Cumulative Problems Solved",
            xaxis_title="Date",
            yaxis_title="Problems Solved",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start solving problems to see progress over time")

def render_problem_card(problem, data_manager, compact=False):
    """Render a problem card with all details"""
    is_solved = problem['id'] in data_manager.progress['solved_problems']
    is_bookmarked = problem['id'] in data_manager.progress['bookmarked_problems']
    
    # Container
    with st.container():
        # Header row
        col1, col2, col3, col4, col5 = st.columns([0.4, 3, 1, 0.8, 0.8])
        
        with col1:
            if is_solved:
                st.markdown("### ✅")
            else:
                st.markdown("### ⬜")
        
        with col2:
            bookmark_icon = "🔖" if is_bookmarked else ""
            st.markdown(f"### {bookmark_icon} [{problem['id']}. {problem['title']}]({problem['link']})")
        
        with col3:
            emoji = get_difficulty_emoji(problem['difficulty'])
            color = get_difficulty_color(problem['difficulty'])
            st.markdown(f"<span style='background:{color}; color:white; padding:4px 12px; border-radius:12px;'>{emoji} {problem['difficulty']}</span>", unsafe_allow_html=True)
        
        with col4:
            if st.button("✓" if not is_solved else "↺", key=f"solve_{problem['id']}", help="Mark as solved/unsolved"):
                if is_solved:
                    data_manager.mark_unsolved(problem['id'])
                else:
                    data_manager.mark_solved(problem['id'])
                st.rerun()
        
        with col5:
            if st.button("⭐" if not is_bookmarked else "★", key=f"bookmark_{problem['id']}", help="Bookmark"):
                data_manager.toggle_bookmark(problem['id'])
                st.rerun()
        
        if not compact:
            # Details row
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Tags
                st.markdown(f"**Topic:** `{problem['topic']}`")
                patterns_html = " ".join([f"<span class='tag'>{p}</span>" for p in problem.get('patterns', [])])
                st.markdown(f"**Patterns:** {patterns_html}", unsafe_allow_html=True)
                
                # Companies
                if problem.get('companies'):
                    companies = ", ".join(problem['companies'][:5])
                    st.caption(f"💼 Asked by: {companies}")
                
                # Complexity
                st.caption(f"⏱️ Time: {problem.get('time_complexity', 'N/A')} | 💾 Space: {problem.get('space_complexity', 'N/A')}")
            
            with col2:
                st.markdown(f"**Importance:** {get_importance_stars(problem['importance'])}")
            
            # Hints (expandable)
            if problem.get('hints'):
                with st.expander("💡 Hints"):
                    for i, hint in enumerate(problem['hints'], 1):
                        st.markdown(f"{i}. {hint}")
            
            # Notes section
            with st.expander("📝 My Notes"):
                note = data_manager.get_note(problem['id'])
                new_note = st.text_area(
                    "Add your notes, approach, or learnings",
                    value=note,
                    key=f"note_{problem['id']}",
                    height=100
                )
                if st.button("Save Note", key=f"save_note_{problem['id']}"):
                    data_manager.save_note(problem['id'], new_note)
                    st.success("Note saved!")
            
            # Related problems
            if problem.get('related_problems'):
                related_ids = problem['related_problems']
                related_titles = [data_manager.get_problem_by_id(rid)['title'] if data_manager.get_problem_by_id(rid) else f"#{rid}" for rid in related_ids]
                st.caption(f"🔗 Related: {', '.join(related_titles)}")
        
        st.markdown("---")

if __name__ == "__main__":
    main()