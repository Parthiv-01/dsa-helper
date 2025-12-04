import json
import os
from datetime import datetime
from typing import List, Dict, Set

class DataManager:
    def __init__(self, config_file='config.json', progress_file='user_progress.json'):
        self.config_file = config_file
        self.progress_file = progress_file
        self.config = self.load_config()
        self.progress = self.load_progress()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.config_file} not found!")
            return {"problems": [], "learning_paths": {}, "topics": [], "patterns": []}
    
    def load_progress(self) -> Dict:
        """Load user progress from JSON file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._create_default_progress()
        return self._create_default_progress()
    
    def _create_default_progress(self) -> Dict:
        """Create default progress structure"""
        return {
            "solved_problems": [],
            "bookmarked_problems": [],
            "notes": {},
            "difficulty_stats": {
                "Easy": 0,
                "Medium": 0,
                "Hard": 0
            },
            "topic_stats": {},
            "last_updated": None,
            "daily_streak": 0,
            "total_time_spent": 0,
            "solve_history": []
        }
    
    def save_progress(self, progress: Dict):
        """Save user progress to JSON file"""
        progress['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2)
    
    def get_all_problems(self) -> List[Dict]:
        """Get all problems from config"""
        return self.config.get('problems', [])
    
    def get_problem_by_id(self, problem_id: int) -> Dict:
        """Get specific problem by ID"""
        for problem in self.config['problems']:
            if problem['id'] == problem_id:
                return problem
        return None
    
    def get_problems_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get problems filtered by difficulty"""
        return [p for p in self.config['problems'] if p['difficulty'] == difficulty]
    
    def get_problems_by_topic(self, topic: str) -> List[Dict]:
        """Get problems filtered by topic"""
        return [p for p in self.config['problems'] if p['topic'] == topic]
    
    def get_problems_by_pattern(self, pattern: str) -> List[Dict]:
        """Get problems filtered by pattern"""
        return [p for p in self.config['problems'] if pattern in p.get('patterns', [])]
    
    def get_learning_path(self, path_name: str) -> Dict:
        """Get specific learning path"""
        return self.config['learning_paths'].get(path_name, {})
    
    def get_all_learning_paths(self) -> Dict:
        """Get all learning paths"""
        return self.config.get('learning_paths', {})
    
    def get_topics(self) -> List[str]:
        """Get all topics"""
        return self.config.get('topics', [])
    
    def get_patterns(self) -> List[str]:
        """Get all patterns"""
        return self.config.get('patterns', [])
    
    def mark_solved(self, problem_id: int, time_spent: int = 0):
        """Mark a problem as solved"""
        if problem_id not in self.progress['solved_problems']:
            self.progress['solved_problems'].append(problem_id)
            
            # Update difficulty stats
            problem = self.get_problem_by_id(problem_id)
            if problem:
                self.progress['difficulty_stats'][problem['difficulty']] += 1
                
                # Update topic stats
                topic = problem['topic']
                self.progress['topic_stats'][topic] = self.progress['topic_stats'].get(topic, 0) + 1
                
                # Add to solve history
                self.progress['solve_history'].append({
                    "problem_id": problem_id,
                    "timestamp": datetime.now().isoformat(),
                    "time_spent": time_spent
                })
            
            self.progress['total_time_spent'] += time_spent
            self.save_progress(self.progress)
    
    def mark_unsolved(self, problem_id: int):
        """Mark a problem as unsolved"""
        if problem_id in self.progress['solved_problems']:
            self.progress['solved_problems'].remove(problem_id)
            
            # Update stats
            problem = self.get_problem_by_id(problem_id)
            if problem:
                self.progress['difficulty_stats'][problem['difficulty']] -= 1
                topic = problem['topic']
                self.progress['topic_stats'][topic] = max(0, self.progress['topic_stats'].get(topic, 0) - 1)
            
            self.save_progress(self.progress)
    
    def toggle_bookmark(self, problem_id: int):
        """Toggle bookmark status of a problem"""
        if problem_id in self.progress['bookmarked_problems']:
            self.progress['bookmarked_problems'].remove(problem_id)
        else:
            self.progress['bookmarked_problems'].append(problem_id)
        self.save_progress(self.progress)
    
    def save_note(self, problem_id: int, note: str):
        """Save note for a problem"""
        self.progress['notes'][str(problem_id)] = {
            "content": note,
            "last_updated": datetime.now().isoformat()
        }
        self.save_progress(self.progress)
    
    def get_note(self, problem_id: int) -> str:
        """Get note for a problem"""
        note_data = self.progress['notes'].get(str(problem_id), {})
        return note_data.get('content', '')
    
    def get_progress_stats(self) -> Dict:
        """Get overall progress statistics"""
        total_problems = len(self.config['problems'])
        solved_count = len(self.progress['solved_problems'])
        
        return {
            "total_problems": total_problems,
            "solved_count": solved_count,
            "unsolved_count": total_problems - solved_count,
            "completion_percentage": (solved_count / total_problems * 100) if total_problems > 0 else 0,
            "difficulty_stats": self.progress['difficulty_stats'],
            "topic_stats": self.progress['topic_stats'],
            "daily_streak": self.progress['daily_streak'],
            "total_time_spent": self.progress['total_time_spent']
        }
    
    def search_problems(self, query: str) -> List[Dict]:
        """Search problems by title or ID"""
        query = query.lower()
        results = []
        for problem in self.config['problems']:
            if (query in problem['title'].lower() or 
                query in str(problem['id']) or
                any(query in pattern.lower() for pattern in problem.get('patterns', []))):
                results.append(problem)
        return results