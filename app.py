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
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
        background: #e3f2fd;
        color: #1976d2;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(to right, #667eea, #764ba2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Data Manager with caching for better performance
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Initialize Session State
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = '🎯 Learning Path'

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
    
    # Main Content
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
        st.markdown("## 📚 Navigation")
        
        view_modes = [
            "🎯 Learning Path",
            "📋 All Problems",
            "📂 By Topic",
            "🔖 Bookmarked",
            "💡 Recommendations",
            "📊 Analytics"
        ]
        
        selected_view = st.radio("View", view_modes, label_visibility="collapsed")
        st.session_state.view_mode = selected_view
        
        st.markdown("---")
        
        # Progress Overview
        st.markdown("### 📈 Quick Stats")
        stats = data_manager.get_progress_stats()
        
        st.progress(stats['completion_percentage'] / 100)
        st.caption(f"{stats['solved_count']} of {stats['total_problems']} solved")
        
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
        
        # Filters
        if selected_view in ["📋 All Problems", "📂 By Topic"]:
            st.markdown("### 🔍 Filters")
            
            difficulties = st.multiselect(
                "Difficulty",
                ['Easy', 'Medium', 'Hard'],
                default=['Easy', 'Medium', 'Hard']
            )
            
            topics = st.multiselect(
                "Topics",
                data_manager.get_topics(),
                default=data_manager.get_topics()
            )
            
            patterns = st.multiselect(
                "Patterns",
                data_manager.get_patterns()
            )
            
            col1, col2 = st.columns(2)
            with col1:
                show_solved = st.checkbox("Solved", value=True)
            with col2:
                show_unsolved = st.checkbox("Unsolved", value=True)
            
            st.session_state.filters = {
                'difficulties': difficulties,
                'topics': topics,
                'patterns': patterns,
                'show_solved': show_solved,
                'show_unsolved': show_unsolved,
                'solved_ids': data_manager.progress['solved_problems']
            }
        
        # Export option
        if selected_view == "📊 Analytics":
            st.markdown("---")
            st.markdown("### 📥 Export")
            if st.button("Export Progress CSV"):
                csv_data = export_progress_to_csv(data_manager)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"leetcode_progress_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
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
        
        with st.expander(
            f"📚 {path_data['name']} - {solved_in_path}/{total_in_path} completed",
            expanded=(completion < 100 and completion >= 0)
        ):
            st.markdown(f"*{path_data['description']}*")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.progress(completion / 100)
            with col2:
                st.markdown(f"**{completion:.0f}%**")
            
            st.markdown("---")
            
            for idx, problem in enumerate(problems):
                # Use problem ID in context to ensure uniqueness
                render_problem_card(problem, context=f"lp_{path_key}_pid{problem['id']}")

def show_all_problems_view():
    st.header("📋 All Problems")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔎 Search problems", "")
    with col2:
        sort_by = st.selectbox("Sort by", ["ID", "Difficulty", "Title"])
    
    if search_query:
        problems = data_manager.search_problems(search_query)
    else:
        problems = data_manager.get_all_problems()
    
    if 'filters' in st.session_state:
        problems = filter_problems(problems, st.session_state.filters)
    
    if sort_by == "ID":
        problems.sort(key=lambda x: x['id'])
    elif sort_by == "Difficulty":
        diff_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        problems.sort(key=lambda x: diff_order[x['difficulty']])
    else:
        problems.sort(key=lambda x: x['title'])
    
    st.markdown(f"**Showing {len(problems)} problems**")
    
    # Pagination for better performance with many problems
    items_per_page = 20
    total_pages = (len(problems) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="all_problems_page")
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        problems_to_show = problems[start_idx:end_idx]
        
        st.caption(f"Showing problems {start_idx + 1}-{min(end_idx, len(problems))} of {len(problems)}")
    else:
        problems_to_show = problems
    
    for idx, problem in enumerate(problems_to_show):
        # Use actual index in full list for unique context
        actual_idx = problems.index(problem) if problem in problems else idx
        render_problem_card(problem, context=f"all_{actual_idx}")

def show_by_topic_view():
    st.header("📂 Problems by Topic")
    
    all_problems = data_manager.get_all_problems()
    
    if 'filters' in st.session_state:
        all_problems = filter_problems(all_problems, st.session_state.filters)
    
    topics = {}
    for problem in all_problems:
        topic = problem['topic']
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(problem)
    
    solved_ids = set(data_manager.progress['solved_problems'])
    
    for topic in sorted(topics.keys()):
        topic_problems = topics[topic]
        solved_in_topic = len([p for p in topic_problems if p['id'] in solved_ids])
        total_in_topic = len(topic_problems)
        
        with st.expander(f"**{topic}** - {solved_in_topic}/{total_in_topic} solved", expanded=False):
            for idx, problem in enumerate(topic_problems):
                # Use problem ID to ensure uniqueness across topics
                render_problem_card(problem, context=f"topic_{topic.replace(' ', '_')}_pid{problem['id']}", compact=True)

def show_bookmarked_view():
    st.header("🔖 Bookmarked Problems")
    
    bookmarked_ids = data_manager.progress['bookmarked_problems']
    
    if not bookmarked_ids:
        st.info("📌 No bookmarked problems yet! Use the ⭐ button to bookmark important problems.")
        return
    
    problems = [data_manager.get_problem_by_id(pid) for pid in bookmarked_ids]
    problems = [p for p in problems if p is not None]
    
    st.markdown(f"**{len(problems)} bookmarked problems**")
    
    for idx, problem in enumerate(problems):
        # Use problem ID for unique keys in bookmarks
        render_problem_card(problem, context=f"bookmark_pid{problem['id']}")

def show_recommendations_view():
    st.header("💡 Recommended for You")
    
    recommended = get_recommended_problems(data_manager, data_manager.progress, limit=10)
    
    if not recommended:
        st.success("🎉 You've solved all high-priority problems! Keep exploring more challenges.")
        st.info("💪 Try solving Medium and Hard problems to further sharpen your skills!")
        return
    
    st.markdown(f"**Top {len(recommended)} problems to solve next:**")
    st.caption("These are high-priority problems based on your progress and difficulty level.")
    
    for i, problem in enumerate(recommended):
        # Use problem ID for unique keys in recommendations
        render_problem_card(problem, context=f"rec_pid{problem['id']}")

def show_analytics_view():
    st.header("📊 Analytics Dashboard")
    
    stats = data_manager.get_progress_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Solved", stats['solved_count'])
    
    with col2:
        st.metric("Completion", f"{stats['completion_percentage']:.1f}%")
    
    with col3:
        streak = calculate_streak(data_manager.progress.get('solve_history', []))
        st.metric("Streak", f"{streak} days")
    
    with col4:
        time_spent = format_time(stats['total_time_spent'])
        st.metric("Time Spent", time_spent)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
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
            },
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
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
                color_continuous_scale='viridis'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start solving problems to see topic statistics")
    
    # Progress over time (if there's solve history)
    if data_manager.progress.get('solve_history'):
        st.markdown("---")
        st.subheader("📈 Progress Over Time")
        
        solve_history = data_manager.progress['solve_history']
        dates = [datetime.fromisoformat(entry['timestamp']).date() for entry in solve_history]
        
        # Count problems solved per day
        date_counts = {}
        for date in dates:
            date_counts[date] = date_counts.get(date, 0) + 1
        
        if date_counts:
            progress_df = pd.DataFrame({
                'Date': list(date_counts.keys()),
                'Problems Solved': list(date_counts.values())
            }).sort_values('Date')
            
            fig = px.line(
                progress_df, 
                x='Date', 
                y='Problems Solved',
                markers=True
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Problems Solved"
            )
            st.plotly_chart(fig, use_container_width=True)

def render_problem_card(problem, context="default", compact=False):
    """Render a problem card"""
    is_solved = problem['id'] in data_manager.progress['solved_problems']
    is_bookmarked = problem['id'] in data_manager.progress['bookmarked_problems']
    
    # Generate unique keys with view mode to prevent duplicates across views
    view_mode = st.session_state.get('view_mode', 'default').replace(' ', '_')
    unique_id = f"{view_mode}_{context}_{problem['id']}"
    solve_key = f"solve_{unique_id}"
    bookmark_key = f"bookmark_{unique_id}"
    
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([0.4, 3, 1, 0.8, 0.8])
        
        with col1:
            st.markdown("### ✅" if is_solved else "### ⬜")
        
        with col2:
            bookmark_icon = "🔖 " if is_bookmarked else ""
            st.markdown(f"### {bookmark_icon}[{problem['id']}. {problem['title']}]({problem['link']})")
        
        with col3:
            emoji = get_difficulty_emoji(problem['difficulty'])
            color = get_difficulty_color(problem['difficulty'])
            st.markdown(
                f"<span style='background:{color}; color:white; padding:4px 12px; "
                f"border-radius:12px;'>{emoji} {problem['difficulty']}</span>",
                unsafe_allow_html=True
            )
        
        with col4:
            if st.button("✓" if not is_solved else "↺", key=solve_key, help="Toggle solved"):
                if is_solved:
                    data_manager.mark_unsolved(problem['id'])
                else:
                    data_manager.mark_solved(problem['id'])
                st.rerun()
        
        with col5:
            if st.button("⭐" if not is_bookmarked else "★", key=bookmark_key, help="Bookmark"):
                data_manager.toggle_bookmark(problem['id'])
                st.rerun()
        
        if not compact:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Topic:** `{problem['topic']}`")
                patterns_html = " ".join([f"<span class='tag'>{p}</span>" for p in problem.get('patterns', [])])
                st.markdown(f"**Patterns:** {patterns_html}", unsafe_allow_html=True)
                
                if problem.get('companies'):
                    companies = ", ".join(problem['companies'][:5])
                    st.caption(f"💼 {companies}")
                
                st.caption(
                    f"⏱️ {problem.get('time_complexity', 'N/A')} | "
                    f"💾 {problem.get('space_complexity', 'N/A')}"
                )
            
            with col2:
                st.markdown(f"**{get_importance_stars(problem['importance'])}**")
            
            if problem.get('hints'):
                with st.expander("💡 Hints"):
                    for i, hint in enumerate(problem['hints'], 1):
                        st.markdown(f"{i}. {hint}")
            
            with st.expander("📝 My Notes"):
                note_key = f"note_{unique_id}"
                save_key = f"save_{unique_id}"
                
                note = data_manager.get_note(problem['id'])
                new_note = st.text_area(
                    "Notes",
                    value=note,
                    key=note_key,
                    height=100,
                    label_visibility="collapsed",
                    placeholder="Write your approach, key insights, or tricky parts..."
                )
                if st.button("Save Note", key=save_key):
                    data_manager.save_note(problem['id'], new_note)
                    st.success("✅ Note saved!")
        
        st.markdown("---")

if __name__ == "__main__":
    main()