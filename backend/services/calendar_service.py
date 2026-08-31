from datetime import datetime, timedelta, timezone
import uuid
from models.schemas import LearnerProfile, RoadmapResponse

class CalendarService:
    @staticmethod
    def generate_ics(roadmap: RoadmapResponse, profile: LearnerProfile) -> str:
        """
        Generates an iCalendar (.ics) string for the given roadmap.
        Distributes the estimated weeks across weekdays.
        """
        now = datetime.now(timezone.utc)
        
        # We start the schedule from the next Monday (or today if it's Monday and early enough)
        # For simplicity, we just start tomorrow at 9 AM.
        start_date = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Create ICS header
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:-//AI Pathfinder//Roadmap {roadmap.roadmap_id}//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:AI Pathfinder: {roadmap.title}",
            "X-WR-TIMEZONE:UTC",
        ]
        
        current_date = start_date
        
        # We will roughly schedule events per milestone
        # If a milestone takes N weeks, we add a weekly recurring event for N weeks.
        for node in roadmap.nodes:
            # Skip completed nodes
            if node.data.status == "completed":
                continue
                
            weeks = max(1, node.data.estimated_weeks)
            
            # Let's create one event per week for this milestone to remind them
            for w in range(weeks):
                event_start = current_date + timedelta(weeks=w)
                event_end = event_start + timedelta(hours=max(1, profile.weekly_hours // 5)) # roughly 1/5 of weekly hours per day?
                
                # We'll just create one block event per week to represent the study focus
                uid = f"{uuid.uuid4()}@aipathfinder.dev"
                dtstamp = now.strftime("%Y%m%dT%H%M%SZ")
                dtstart = event_start.strftime("%Y%m%dT%H%M%SZ")
                dtend = event_end.strftime("%Y%m%dT%H%M%SZ")
                
                summary = f"Study: {node.data.label}"
                res_title = node.data.primary_resource.title if node.data.primary_resource else "Documentation"
                res_url = node.data.primary_resource.url if node.data.primary_resource else "https://aipathfinder.dev"
                description = f"Focus for this week: {node.data.description}\\nRecommended Resource: {res_title} - {res_url}"
                
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{dtstamp}",
                    f"DTSTART:{dtstart}",
                    f"DTEND:{dtend}",
                    f"SUMMARY:{summary}",
                    f"DESCRIPTION:{description}",
                    "END:VEVENT"
                ])
                
            # Advance current date by the number of weeks for the next sequential node
            current_date += timedelta(weeks=weeks)
            
        ics_lines.append("END:VCALENDAR")
        
        return "\r\n".join(ics_lines)
