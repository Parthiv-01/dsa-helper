import streamlit as st
from datetime import datetime, timedelta

def get_difficulty_color(difficulty: str) -> str:
    """Get color for difficulty level"""
    colors = {
        "Easy": "#00b8a9",
        "Medium": "#f8b500",
        "Hard": "#e63946"
    }
    return colors.get(difficulty, "#666")

def get_difficulty_emoji(difficulty: str) -> str:
    """Get emoji for difficulty level"""
    emojis = {
        "Easy": "🟢",
        "Medium": "🟡",
        "Hard": "🔴"
    }
    return emojis.get(difficulty, "⚪")

def get_importance_stars(importance: str) -> str:
    """Get star rating for importance"""
    if importance == "High":
        return "⭐⭐⭐"
    elif importance == "Medium":
        return "⭐⭐"
    else:
        return "⭐"

def format_time(minutes: int) -> str:
    """Format time in readable format"""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"

def calculate_streak(solve_history: list) -> int:
    """Calculate current solving streak"""
    if not solve_history:
        return 0
    
    # Sort by timestamp
    sorted_history = sorted(solve_history, key=lambda x: x['timestamp'], reverse=True)
    
    streak = 0
    current_date = datetime.now().date()
    
    for entry in sorted_history:
        entry_date = datetime.fromisoformat(entry['timestamp']).date()
        
        if entry_date == current_date or entry_date == current_date - timedelta(days=streak):
            if entry_date < current_date:
                streak += 1
                current_date = entry_date
        else:
            break
    
    return streak

def filter_problems(problems: list, filters: dict) -> list:
    """Filter problems based on multiple criteria"""
    filtered = problems
    
    # Filter by difficulty
    if filters.get('difficulties'):
        filtered = [p for p in filtered if p['difficulty'] in filters['difficulties']]
    
    # Filter by topics
    if filters.get('topics'):
        filtered = [p for p in filtered if p['topic'] in filters['topics']]
    
    # Filter by patterns
    if filters.get('patterns'):
        filtered = [p for p in filtered if any(pattern in p.get('patterns', []) for pattern in filters['patterns'])]
    
    # Filter by companies
    if filters.get('companies'):
        filtered = [p for p in filtered if any(company in p.get('companies', []) for company in filters['companies'])]
    
    # Filter by solved status
    solved_ids = filters.get('solved_ids', [])
    if filters.get('show_solved') == False:
        filtered = [p for p in filtered if p['id'] not in solved_ids]
    if filters.get('show_unsolved') == False:
        filtered = [p for p in filtered if p['id'] in solved_ids]
    
    return filtered

def get_recommended_problems(data_manager, user_progress, limit=5):
    """Get recommended problems based on user progress"""
    all_problems = data_manager.get_all_problems()
    solved_ids = set(user_progress['solved_problems'])
    unsolved = [p for p in all_problems if p['id'] not in solved_ids]
    
    # Prioritize high importance unsolved problems
    high_importance = [p for p in unsolved if p['importance'] == 'High']
    
    # Sort by difficulty (Easy first for beginners)
    difficulty_order = {'Easy': 1, 'Medium': 2, 'Hard': 3}
    high_importance.sort(key=lambda x: difficulty_order[x['difficulty']])
    
    return high_importance[:limit]

def export_progress_to_csv(data_manager):
    """Export progress to CSV format"""
    import pandas as pd
    from io import StringIO
    
    problems = data_manager.get_all_problems()
    solved_ids = set(data_manager.progress['solved_problems'])
    
    data = []
    for p in problems:
        data.append({
            'ID': p['id'],
            'Title': p['title'],
            'Difficulty': p['difficulty'],
            'Topic': p['topic'],
            'Status': 'Solved' if p['id'] in solved_ids else 'Unsolved',
            'Link': p['link']
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def style_metric_card(label: str, value: str, delta: str = None):
    """Create styled metric card"""
    delta_html = f'<p style="color: #00b8a9; margin: 0;">{delta}</p>' if delta else ''
    
    return f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <p style="margin: 0; font-size: 14px; opacity: 0.9;">{label}</p>
        <h2 style="margin: 10px 0; font-size: 32px;">{value}</h2>
        {delta_html}
    </div>
    """