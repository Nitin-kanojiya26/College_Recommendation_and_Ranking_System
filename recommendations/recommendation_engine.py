class RecommendationEngine:
    
    @staticmethod
    def calculate_scores(student, college):
        """Calculate all component scores"""
        scores = {}
        
        # 1. Cutoff Score (30%)
        cutoff = college.get_cutoff(student.category)
        if student.marks >= cutoff:
            scores['cutoff'] = 30
        else:
            # Linear penalty for missing cutoff
            penalty = (cutoff - student.marks) * 0.5
            scores['cutoff'] = max(0, 30 - penalty)
        
        # 2. Course Match (20%)
        common_courses = set(student.preferred_courses) & set(college.courses_offered)
        if common_courses:
            scores['course'] = 20
        elif student.preferred_courses and college.courses_offered:
            scores['course'] = 10
        else:
            scores['course'] = 5
        
        # 3. Location (10%)
        if student.preferred_location and student.preferred_location.lower() == college.location.lower():
            scores['location'] = 10
        else:
            scores['location'] = 5
        
        # 4. Budget Fit (10%)
        if student.budget >= college.annual_fees:
            scores['budget'] = 10
        else:
            # Penalty based on how much over budget
            overshoot = college.annual_fees - student.budget
            penalty = overshoot * 0.001  # 0.1% penalty per unit overshoot
            scores['budget'] = max(0, 10 - penalty)
        
        # 5. Placements (15%)
        placement_score = (college.placement_rate * 0.08) + (college.avg_package * 0.5)
        scores['placement'] = min(15, placement_score)
        
        # 6. Facilities (5%)
        scores['facility'] = min(5, len(college.facilities) * 0.5)
        
        # 7. Reviews (10%)
        scores['review'] = college.review_score * 2
        
        return scores
    
    @staticmethod
    def calculate_total_score(scores):
        """Calculate total score out of 10"""
        total = sum(scores.values())
        return round((total / 100) * 10, 2)
    
    @staticmethod
    def calculate_star_rating(total_score):
        """Convert 0-10 score to 0-5 stars"""
        return round(total_score / 2, 1)