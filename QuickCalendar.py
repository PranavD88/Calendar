import datetime
from PIL import Image, ImageDraw, ImageFont


class Calendar:
    def __init__(self):
        self.events = {}
        self.event_colors = {}  # Dictionary for light colors so that the text is always visible
        self.color_palette = [
            (173, 216, 230),  # Light blue
            (144, 238, 144),  # Light green
            (255, 182, 193),  # Light pink
            (255, 239, 213),  # Light yellow
            (240, 230, 140),  # Khaki
            (221, 160, 221),  # Plum
            (135, 206, 250),  # Light sky blue
            (255, 228, 196),  # Bisque
            (175, 238, 238),  # Pale turquoise
            (240, 255, 240),  # Honeydew
        ]
        self.color_index = 0

    def add_event(self, date, event):
        if date not in self.events:
            self.events[date] = []
        self.events[date].append(event)

    def add_event_check(self, date, event):
        if date in self.events and event in self.events[date]:
            confirmation = input(f"'{event}' is already scheduled for {date.strftime('%B %d, %Y')}. Are you sure you want to add it again? (yes/no): ").strip().lower()
            if confirmation != "yes":
                print("Event not added.")
                return
        self.add_event(date, event)

        if event not in self.event_colors:
            self.event_colors[event] = self.color_palette[self.color_index]
            self.color_index = (self.color_index + 1) % len(self.color_palette)

        print(f"Event '{event}' added to {date.strftime('%B %d, %Y')}.")

    def get_events_for_day(self, date):
        return self.events.get(date, [])

    def generate_month_image(self, year, month):
        cell_width, cell_height = 220, 200
        x_start, y_start = 50, 120

        start_date = datetime.date(year, month, 1)
        if month == 12:
            next_month_start = datetime.date(year + 1, 1, 1)
        else:
            next_month_start = datetime.date(year, month + 1, 1)
        days_in_month = (next_month_start - start_date).days
        day_of_week = (start_date.weekday() + 1) % 7
        total_cells = days_in_month + day_of_week
        rows_needed = (total_cells + 6) // 7

        img_width = 1800
        img_height = y_start + (rows_needed + 1) * cell_height + 100
        img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Fonts
        try:
            font_title = ImageFont.truetype("arial.ttf", 60)
            font_header = ImageFont.truetype("arial.ttf", 40)
            font_text = ImageFont.truetype("arial.ttf", 18)
        except IOError:
            font_title = font_header = font_text = ImageFont.load_default()

        month_name = datetime.date(year, month, 1).strftime('%B %Y')
        draw.text((img_width // 2 - 150, 20), month_name, font=font_title, fill=(0, 0, 0))

        days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days_of_week):
            x_pos = x_start + i * cell_width
            draw.text((x_pos + 10, y_start), day, font=font_header, fill=(0, 0, 0))

        current_date = start_date
        x_offset, y_offset = x_start + day_of_week * cell_width, y_start + cell_height
        for day in range(1, days_in_month + 1):
            draw.rectangle([x_offset, y_offset, x_offset + cell_width, y_offset + cell_height],
                           outline="black", fill=(240, 240, 240))
            draw.text((x_offset + 10, y_offset + 10), str(day), font=font_text, fill=(0, 0, 0))

            # Event Adder
            events = self.get_events_for_day(current_date)
            event_y_offset = y_offset + 35
            for event in events:
                words = event.split()
                lines = []
                line = ""
                for word in words:
                    if draw.textlength(line + word, font=font_text) < cell_width - 20:
                        line += f"{word} "
                    else:
                        lines.append(line.strip())
                        line = f"{word} "
                if line:
                    lines.append(line.strip())

                box_height = len(lines) * 25 + 10
                event_color = self.event_colors.get(event, (173, 216, 230))
                draw.rectangle(
                    [x_offset + 10, event_y_offset, x_offset + cell_width - 10, event_y_offset + box_height],
                    fill=event_color, outline="black")

                line_y_offset = event_y_offset + 5
                for line in lines:
                    draw.text((x_offset + 15, line_y_offset), line, font=font_text, fill=(0, 0, 0))
                    line_y_offset += 25
                event_y_offset += box_height + 5

            x_offset += cell_width
            if (day_of_week + 1) % 7 == 0:
                x_offset = x_start
                y_offset += cell_height
            current_date += datetime.timedelta(days=1)
            day_of_week = (day_of_week + 1) % 7

        img.save(f"calendar_{year}_{month}.png")
        img.show()


def get_dates_for_weekday(year, month, weekday_name):
    """Get all dates in the given month that fall on a specific weekday"""
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    if weekday_name not in weekdays:
        return []

    weekday_index = weekdays.index(weekday_name)
    start_date = datetime.date(year, month, 1)
    days_in_month = (datetime.date(year, month + 1, 1) if month < 12 else datetime.date(year + 1, 1, 1)) - start_date
    matching_dates = [
        start_date + datetime.timedelta(days=i)
        for i in range(days_in_month.days)
        if (start_date + datetime.timedelta(days=i)).weekday() == weekday_index
    ]
    return matching_dates


def main():
    # User Prompt
    print("Enter events for the calendar. Type 'done' when finished.")
    my_calendar = Calendar()
    year = int(input("Enter the year for the calendar (e.g., 2025): "))
    month = int(input("Enter the month for the calendar (1-12): "))

    while True:
        date_input = input("Enter the date or weekday for the event (e.g., 'Monday' or '15', or 'done' to finish): ").strip()
        if date_input.lower() == "done":
            break

        if date_input.isdigit():
            day = int(date_input)
            try:
                event_date = datetime.date(year, month, day)
                event_description = input(f"Enter the event description for {event_date.strftime('%B %d, %Y')}: ").strip()
                my_calendar.add_event_check(event_date, event_description)
            except ValueError:
                print("Invalid date. Please enter a valid day number.")
        else:
            dates = get_dates_for_weekday(year, month, date_input)
            if dates:
                event_description = input(f"Enter the event description for all {date_input}s in {datetime.date(year, month, 1).strftime('%B')}: ").strip()
                for date in dates:
                    my_calendar.add_event_check(date, event_description)
            else:
                print("Invalid weekday. Please enter a valid day name (e.g., 'Monday').")

    my_calendar.generate_month_image(year, month)
    print(f"Calendar for {datetime.date(year, month, 1).strftime('%B %Y')} generated as 'calendar_{year}_{month}.png'.")


if __name__ == "__main__":
    main()