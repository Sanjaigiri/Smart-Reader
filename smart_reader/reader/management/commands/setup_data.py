from django.core.management.base import BaseCommand
from reader.models import Category, Tag, Achievement, Article
from django.contrib.auth.models import User
import random


class Command(BaseCommand):
    help = 'Setup initial data for SmartReader (categories, tags, achievements, 500+ articles)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up initial data with 500+ articles...')
        
        # Create Categories
        categories_data = [
            {'name': 'Classic Literature', 'slug': 'classic-literature', 'description': 'Timeless literary works from renowned authors', 'icon': 'fa-book', 'color': '#6366f1'},
            {'name': 'Educational Materials', 'slug': 'educational-materials', 'description': 'Learning resources and academic content', 'icon': 'fa-graduation-cap', 'color': '#10b981'},
            {'name': 'Self Development', 'slug': 'self-development', 'description': 'Personal growth and self-improvement', 'icon': 'fa-user-graduate', 'color': '#f59e0b'},
            {'name': 'Science & Technology', 'slug': 'science-technology', 'description': 'Scientific discoveries and tech innovations', 'icon': 'fa-flask', 'color': '#3b82f6'},
            {'name': 'Business & Finance', 'slug': 'business-finance', 'description': 'Business strategies and financial wisdom', 'icon': 'fa-briefcase', 'color': '#ef4444'},
            {'name': 'Philosophy', 'slug': 'philosophy', 'description': 'Deep thinking and philosophical works', 'icon': 'fa-brain', 'color': '#8b5cf6'},
            {'name': 'History', 'slug': 'history', 'description': 'Historical events and biographies', 'icon': 'fa-landmark', 'color': '#ec4899'},
            {'name': 'Fiction', 'slug': 'fiction', 'description': 'Imaginative and creative stories', 'icon': 'fa-feather-alt', 'color': '#14b8a6'},
            {'name': 'Health & Wellness', 'slug': 'health-wellness', 'description': 'Physical and mental health resources', 'icon': 'fa-heartbeat', 'color': '#ef4444'},
            {'name': 'Psychology', 'slug': 'psychology', 'description': 'Understanding the human mind', 'icon': 'fa-brain', 'color': '#a855f7'},
        ]
        
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
            if created:
                self.stdout.write(f'  Created category: {cat.name}')
        
        # Create Tags
        tags_data = [
            {'name': 'Motivation', 'slug': 'motivation'}, {'name': 'Success', 'slug': 'success'},
            {'name': 'Leadership', 'slug': 'leadership'}, {'name': 'Productivity', 'slug': 'productivity'},
            {'name': 'Money', 'slug': 'money'}, {'name': 'Investing', 'slug': 'investing'},
            {'name': 'Mindset', 'slug': 'mindset'}, {'name': 'Communication', 'slug': 'communication'},
            {'name': 'Creativity', 'slug': 'creativity'}, {'name': 'Health', 'slug': 'health'},
            {'name': 'Habits', 'slug': 'habits'}, {'name': 'Learning', 'slug': 'learning'},
            {'name': 'Relationships', 'slug': 'relationships'}, {'name': 'Career', 'slug': 'career'},
            {'name': 'Technology', 'slug': 'technology'},
        ]
        
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(slug=tag_data['slug'], defaults=tag_data)
            if created:
                self.stdout.write(f'  Created tag: {tag.name}')
        
        # Create Achievements
        achievements_data = [
            {'name': 'First Article', 'description': 'Complete your first article', 'icon': 'fa-star', 'badge_color': '#10b981', 'requirement_type': 'articles_read', 'requirement_value': 1},
            {'name': 'Bookworm', 'description': 'Complete 5 articles', 'icon': 'fa-book', 'badge_color': '#3b82f6', 'requirement_type': 'articles_read', 'requirement_value': 5},
            {'name': 'Scholar', 'description': 'Complete 10 articles', 'icon': 'fa-graduation-cap', 'badge_color': '#8b5cf6', 'requirement_type': 'articles_read', 'requirement_value': 10},
            {'name': 'Master Reader', 'description': 'Complete 25 articles', 'icon': 'fa-crown', 'badge_color': '#f59e0b', 'requirement_type': 'articles_read', 'requirement_value': 25},
            {'name': 'Century Reader', 'description': 'Complete 100 articles', 'icon': 'fa-award', 'badge_color': '#ef4444', 'requirement_type': 'articles_read', 'requirement_value': 100},
            {'name': 'Week Warrior', 'description': 'Maintain a 7-day reading streak', 'icon': 'fa-fire', 'badge_color': '#ef4444', 'requirement_type': 'streak_days', 'requirement_value': 7},
            {'name': 'Month Master', 'description': 'Maintain a 30-day reading streak', 'icon': 'fa-medal', 'badge_color': '#cd7f32', 'requirement_type': 'streak_days', 'requirement_value': 30},
            {'name': 'Dedicated Reader', 'description': 'Spend 1 hour reading', 'icon': 'fa-clock', 'badge_color': '#6366f1', 'requirement_type': 'time_spent', 'requirement_value': 3600},
        ]
        
        for ach_data in achievements_data:
            ach, created = Achievement.objects.get_or_create(name=ach_data['name'], defaults=ach_data)
            if created:
                self.stdout.write(f'  Created achievement: {ach.name}')
        
        # Create 500+ articles
        self.create_all_articles()
        
        total = Article.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Setup complete! Total articles: {total}'))
    
    def create_all_articles(self):
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@smartreader.com', 'is_staff': True, 'is_superuser': True}
        )
        
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())
        difficulties = ['beginner', 'intermediate', 'advanced']
        
        content_template = self.get_content_template()
        books = self.get_all_books()
        
        count = 0
        for cat_slug, book_list in books.items():
            try:
                category = Category.objects.get(slug=cat_slug)
            except Category.DoesNotExist:
                category = random.choice(categories)
            
            for title, author, summary in book_list:
                slug = self.make_slug(title)
                if Article.objects.filter(slug=slug).exists():
                    continue
                
                content = content_template.format(title=title, author=author, summary=summary)
                article = Article.objects.create(
                    title=f"{title} - Key Insights",
                    slug=slug,
                    author=admin_user,
                    content=content,
                    summary=f"{summary}. Based on {author}'s work.",
                    category=category,
                    difficulty=random.choice(difficulties),
                    estimated_read_time=random.randint(8, 20),
                    is_published=True,
                    is_featured=random.random() < 0.1,
                )
                article.tags.set(random.sample(tags, k=min(3, len(tags))))
                count += 1
        
        # Add extra articles to reach 500+
        self.create_extra_articles(admin_user, categories, tags, difficulties, count)
    
    def make_slug(self, title):
        return title.lower().replace(' ', '-').replace("'", '').replace(',', '').replace('.', '').replace('*', '').replace('!', '').replace('?', '').replace(':', '').replace('/', '-')[:50]
    
    def get_content_template(self):
        return '''# {title}
## By {author}

{summary}

---

## Chapter 1: Introduction

This comprehensive guide explores the profound concepts and life-changing principles from "{title}" by {author}. Whether you are new to this topic or seeking deeper understanding, this detailed article provides essential insights that can transform your perspective and approach to life.

The work of {author} has influenced millions of people worldwide, and for good reason. The ideas presented here are not mere theories but battle-tested principles that have stood the test of time. As we delve into this material, you will discover actionable wisdom that you can apply immediately to your own life.

Throughout history, great thinkers have understood that knowledge without application is merely entertainment. {author} takes this wisdom further by providing not just the "what" but the crucial "how" - the practical steps that bridge the gap between understanding and transformation.

### Why This Work Matters

In our fast-paced modern world, we are constantly bombarded with information. What sets truly great works apart is their ability to cut through the noise and provide clarity. "{title}" does exactly this - it distills complex ideas into accessible, actionable principles.

The relevance of this work extends beyond any single domain. Whether you are a student, professional, entrepreneur, or simply someone seeking personal growth, the principles discussed here apply universally. They speak to fundamental truths about human nature, success, and fulfillment.

---

## Chapter 2: The Foundation Principles

### Understanding Core Concepts

The foundational principles presented by {author} form the bedrock upon which all other concepts rest. Without a solid understanding of these basics, the more advanced ideas would lack context and meaning.

At its core, this work addresses the fundamental question that has occupied philosophers and practical thinkers throughout history: How do we live a meaningful and successful life? The answer, as {author} demonstrates, lies not in any single action but in the consistent application of sound principles over time.

### The First Principle: Awareness

Everything begins with awareness. You cannot change what you do not acknowledge. {author} emphasizes the critical importance of honest self-assessment as the starting point for any meaningful transformation.

This awareness extends to multiple dimensions:
- Self-awareness: Understanding your strengths, weaknesses, values, and motivations
- Situational awareness: Recognizing the context in which you operate
- Consequential awareness: Understanding how your actions affect yourself and others
- Temporal awareness: Recognizing both immediate and long-term impacts

Without this foundation of awareness, even the best strategies will fail. It is like trying to navigate without knowing your current position - impossible and frustrating.

### The Second Principle: Intentionality

Once awareness is established, {author} guides us toward intentionality. This means moving from reactive to proactive living. Instead of being buffeted by circumstances, we learn to shape them according to our values and goals.

Intentionality requires:
1. Clear definition of what you want
2. Understanding why you want it
3. Commitment to the process required
4. Willingness to sacrifice lesser goals for greater ones
5. Patience with the timeline required

Many people fail not because they lack ability but because they lack intentionality. They drift through life responding to whatever demands attention rather than directing their energy toward what truly matters.

### The Third Principle: Consistency

Perhaps the most underrated principle is consistency. {author} makes a compelling case that extraordinary results come not from extraordinary actions but from ordinary actions performed with extraordinary consistency.

The mathematics of consistency are remarkable. Small improvements, compounded daily, lead to massive results over time. A 1% improvement daily results in being 37 times better after one year. Conversely, 1% daily decline leads to near-total degradation.

This principle applies universally:
- Physical fitness: Daily exercise beats occasional intense workouts
- Skill development: Regular practice trumps sporadic cramming
- Relationships: Consistent small gestures outweigh occasional grand ones
- Financial growth: Regular saving beats lottery-ticket thinking

---

## Chapter 3: Practical Applications

### Implementing the Principles

Understanding principles is necessary but insufficient. {author} dedicates significant attention to practical implementation, recognizing that the gap between knowing and doing is where most people fail.

The implementation framework follows a specific sequence:

**Step 1: Start Small**
Begin with the smallest possible action that moves you in the right direction. The goal at this stage is not transformation but momentum. A tiny step, consistently taken, builds the foundation for larger ones.

For example, if your goal is to develop a reading habit, do not start with an hour daily. Start with one page. The psychological barrier to reading one page is almost nonexistent, yet this small action begins building the neural pathways and identity associated with being a reader.

**Step 2: Build Systems**
{author} distinguishes between goals and systems. Goals define direction; systems determine progress. Winners and losers often have the same goals - what separates them is their systems.

A system is a reliable process that makes progress inevitable. It removes the need for motivation or willpower, both of which are limited resources. Good systems work even when you do not feel like it.

**Step 3: Track Progress**
What gets measured gets managed. {author} recommends simple but consistent tracking of key metrics. This tracking serves multiple purposes:
- Provides feedback on what is working
- Creates accountability
- Maintains motivation through visible progress
- Enables course correction when needed

**Step 4: Adjust and Iterate**
No plan survives first contact with reality unchanged. The key is not perfect planning but rapid iteration. Try something, observe results, adjust, repeat. This cycle of continuous improvement is more valuable than any static strategy.

### Real-World Examples

{author} provides numerous case studies demonstrating these principles in action. Consider the example of successful individuals who have applied these concepts:

**Example 1: The Entrepreneur**
A business founder applies awareness by honestly assessing market conditions and personal capabilities. Intentionality guides the selection of which opportunity to pursue. Consistency manifests in showing up every day despite setbacks. Systems ensure that key activities happen regardless of mood.

**Example 2: The Student**
A student applies awareness by understanding their learning style and knowledge gaps. Intentionality means choosing which subjects deserve focus. Consistency appears in daily study habits. Systems include scheduled review sessions and active learning techniques.

**Example 3: The Professional**
A career-focused individual applies awareness by understanding organizational dynamics and personal brand. Intentionality guides career decisions and skill development. Consistency shows in reliable high-quality work. Systems ensure continuous learning and network maintenance.

---

## Chapter 4: Overcoming Challenges

### Common Obstacles

{author} acknowledges that the path to applying these principles is not smooth. Several common obstacles arise:

**Challenge 1: Resistance to Change**
Human beings are creatures of habit. Our brains are wired to conserve energy by defaulting to established patterns. Change requires conscious effort, which the brain interprets as a threat to efficiency.

The solution involves:
- Making changes small enough to avoid triggering resistance
- Linking new behaviors to established ones
- Creating environmental cues that prompt desired actions
- Building identity around the new behavior

**Challenge 2: Lack of Immediate Results**
We live in an instant gratification culture. The principles described here work through compound effects, which means results may not be visible for weeks or months.

{author} advises:
- Focus on leading indicators (actions) rather than lagging indicators (results)
- Trust the process when the outcome is not yet visible
- Celebrate small wins along the way
- Connect with others on the same journey for support

**Challenge 3: Environmental Pressures**
Your environment exerts enormous influence on your behavior. If your surroundings do not support your goals, success becomes exponentially harder.

Environmental design strategies include:
- Removing friction for desired behaviors
- Adding friction for undesired behaviors
- Surrounding yourself with people who embody your aspirations
- Creating physical spaces that support your goals

**Challenge 4: Competing Priorities**
Life presents endless demands on your time and attention. Without clear priorities, everything seems urgent and important.

{author} recommends:
- Defining your non-negotiables
- Learning to say no to good opportunities to preserve great ones
- Scheduling priorities rather than prioritizing your schedule
- Regular review to ensure alignment between actions and values

---

## Chapter 5: Deep Insights

### The Power of Compound Effects

One of the most powerful concepts {author} presents is the compound effect. This principle operates in every area of life, often invisibly.

Consider knowledge: Every new piece of information you acquire connects with existing knowledge, creating new insights. A person who reads daily for years develops not just more knowledge but qualitatively different understanding than someone with the same IQ who does not read.

Consider relationships: Small consistent investments in relationships compound into deep trust and connection that cannot be manufactured through occasional grand gestures.

Consider skills: Daily practice creates not just incremental improvement but eventual mastery that seems almost magical to observers.

The compound effect works in negative directions too. Small negative habits - poor diet, negative thinking, avoiding challenges - compound into significant problems over time.

### The Identity Framework

{author} introduces a powerful framework around identity. Most behavior change efforts fail because they focus on outcomes or processes rather than identity.

The three layers of behavior change are:
1. Outcomes: What you get
2. Processes: What you do
3. Identity: What you believe about yourself

Effective lasting change works from the inside out. When you shift your identity to "I am a healthy person," healthy behaviors follow naturally. When you see yourself as "a reader," finding time to read becomes automatic.

This identity-based approach explains why some people seem to have endless willpower while others struggle constantly. The former have aligned their identity with their goals; for them, the desired behavior is simply who they are.

### The Environment Principle

Your environment is more powerful than your willpower. {author} presents compelling evidence that environment design is often more effective than motivation or discipline.

Key environmental factors include:
- Physical surroundings and what behaviors they facilitate
- Social environment and the norms it establishes
- Information environment and what ideas you are exposed to
- Digital environment and how it directs your attention

Smart environment design means:
- Making desired behaviors obvious and easy
- Making undesired behaviors invisible and hard
- Surrounding yourself with people who exemplify your aspirations
- Curating your information inputs carefully

---

## Chapter 6: Practical Exercises

### Exercise 1: The Awareness Audit

Take time to honestly assess your current situation across key life areas:
- Health and physical energy
- Relationships and social connections
- Career and professional development
- Financial situation and security
- Personal growth and learning
- Contribution and meaning

Rate each area on a scale of 1-10. Identify the one or two areas where improvement would have the greatest positive impact on your overall life.

### Exercise 2: Values Clarification

List your top 10 values. Then force-rank them by asking: "If I could only have one of these, which would it be?" Repeat until you have a clear hierarchy.

Use this hierarchy to evaluate how you actually spend your time. Is there alignment or disconnect? What changes would bring greater alignment?

### Exercise 3: System Design

Choose one goal you want to achieve. Instead of focusing on the outcome, design a system that makes progress inevitable:
- What daily action would virtually guarantee success over time?
- How can you make this action automatic?
- What environmental changes would support this action?
- How will you track consistency?

### Exercise 4: Identity Statement

Write a clear statement of who you are becoming. Use present tense: "I am..." rather than "I will be..."

Examples:
- "I am someone who takes care of their body"
- "I am a person who shows up consistently"
- "I am someone who adds value to others"

Review this statement daily and use it to guide decisions.

### Exercise 5: Environment Audit

Walk through your physical space with fresh eyes. Ask:
- What does this environment make easy?
- What does it make hard?
- What behaviors does it prompt?
- What could I change to better support my goals?

Make at least three environmental changes this week.

---

## Chapter 7: Key Takeaways

### Summary of Core Ideas

As we conclude our exploration of "{title}" by {author}, let us consolidate the key learnings:

1. **Success is a process, not an event.** There are no overnight successes, only overnight recognitions of long-term consistent effort.

2. **Small actions compound into massive results.** The key is not the size of individual actions but their consistency over time.

3. **Systems beat goals.** While goals provide direction, systems provide the mechanism for actual progress.

4. **Environment shapes behavior.** Design your surroundings to make desired behaviors automatic.

5. **Identity drives action.** Lasting change comes from shifting who you believe yourself to be.

6. **Awareness precedes transformation.** You cannot change what you do not acknowledge.

7. **Patience is essential.** Compound effects take time to become visible. Trust the process.

8. **Learning is continuous.** The principles presented here are starting points, not destinations.

### Final Thoughts

"{title}" offers transformative insights that have the power to change your life - but only if you apply them. The key is not just reading, but implementing consistently over time.

{author} reminds us that knowledge without action is merely entertainment. The principles discussed here are simple but not easy. They require commitment, patience, and persistence.

Start today. Start small. But start.

The journey of a thousand miles begins with a single step. Take that step now.

---

## Appendix: Further Reading

For those who wish to explore these concepts further, consider:
- The original work: "{title}" by {author}
- Related works in this field
- Practical workbooks and exercises
- Communities of others applying these principles

Remember: The goal is not to read more books but to apply what you learn from the ones you do read.

---

*This comprehensive summary covers the key concepts from "{title}" by {author}. For the complete experience, including additional examples, detailed case studies, and the full depth of the author's insights, we recommend reading the original work.*

*Reading time: approximately 25-30 minutes*
*Word count: approximately 2,500 words*'''

    def get_all_books(self):
        return {
            'self-development': [
                ('Atomic Habits', 'James Clear', 'Building good habits and breaking bad ones'),
                ('The 7 Habits of Highly Effective People', 'Stephen Covey', 'Principles of personal effectiveness'),
                ('Think and Grow Rich', 'Napoleon Hill', 'The power of personal beliefs'),
                ('How to Win Friends and Influence People', 'Dale Carnegie', 'Handling people effectively'),
                ('The Power of Now', 'Eckhart Tolle', 'Living in the present moment'),
                ('Mindset', 'Carol Dweck', 'The growth mindset concept'),
                ('The Subtle Art of Not Giving a Fck', 'Mark Manson', 'Counterintuitive approach to living'),
                ('Awaken the Giant Within', 'Tony Robbins', 'Control your destiny'),
                ('The Power of Habit', 'Charles Duhigg', 'Why we do what we do'),
                ('Deep Work', 'Cal Newport', 'Rules for focused success'),
                ('The Miracle Morning', 'Hal Elrod', 'Transform your life before 8AM'),
                ('You Are a Badass', 'Jen Sincero', 'Stop doubting your greatness'),
                ('The Four Agreements', 'Don Miguel Ruiz', 'Guide to personal freedom'),
                ('Grit', 'Angela Duckworth', 'Power of passion and perseverance'),
                ('Emotional Intelligence', 'Daniel Goleman', 'Why EQ matters more than IQ'),
                ('The 5 AM Club', 'Robin Sharma', 'Own your morning'),
                ('Outliers', 'Malcolm Gladwell', 'The story of success'),
                ('The Compound Effect', 'Darren Hardy', 'Jumpstart your success'),
                ('Make Your Bed', 'William McRaven', 'Little things that change life'),
                ('Cant Hurt Me', 'David Goggins', 'Master your mind'),
                ('12 Rules for Life', 'Jordan Peterson', 'Antidote to chaos'),
                ('The Obstacle Is the Way', 'Ryan Holiday', 'Turning trials into triumph'),
                ('Ego Is the Enemy', 'Ryan Holiday', 'Fight your greatest opponent'),
                ('Stillness Is the Key', 'Ryan Holiday', 'Ancient strategy for modern life'),
                ('The Daily Stoic', 'Ryan Holiday', 'Meditations on wisdom'),
            ],
            'business-finance': [
                ('Rich Dad Poor Dad', 'Robert Kiyosaki', 'What the rich teach about money'),
                ('The Intelligent Investor', 'Benjamin Graham', 'Value investing guide'),
                ('Good to Great', 'Jim Collins', 'Why companies make the leap'),
                ('Zero to One', 'Peter Thiel', 'Notes on startups'),
                ('The Lean Startup', 'Eric Ries', 'Continuous innovation'),
                ('Start with Why', 'Simon Sinek', 'How leaders inspire action'),
                ('The 4-Hour Workweek', 'Tim Ferriss', 'Escape 9-5 live anywhere'),
                ('The E-Myth Revisited', 'Michael Gerber', 'Why small businesses fail'),
                ('Built to Last', 'Jim Collins', 'Habits of visionary companies'),
                ('The Hard Thing About Hard Things', 'Ben Horowitz', 'Building a business'),
                ('Principles', 'Ray Dalio', 'Life and work principles'),
                ('The Millionaire Next Door', 'Thomas Stanley', 'Secrets of the wealthy'),
                ('I Will Teach You to Be Rich', 'Ramit Sethi', '6-week money program'),
                ('The Total Money Makeover', 'Dave Ramsey', 'Plan for financial fitness'),
                ('The Psychology of Money', 'Morgan Housel', 'Lessons on wealth'),
                ('Thinking Fast and Slow', 'Daniel Kahneman', 'How we decide'),
                ('Freakonomics', 'Steven Levitt', 'Hidden side of everything'),
                ('The Richest Man in Babylon', 'George Clason', 'Ancient success secrets'),
                ('Your Money or Your Life', 'Vicki Robin', 'Transform money relationship'),
                ('The Little Book of Common Sense Investing', 'John Bogle', 'Guarantee fair share'),
                ('A Random Walk Down Wall Street', 'Burton Malkiel', 'Investment strategies'),
                ('The Warren Buffett Way', 'Robert Hagstrom', 'Buffett strategies'),
                ('One Up On Wall Street', 'Peter Lynch', 'Use what you know'),
                ('The Essays of Warren Buffett', 'Warren Buffett', 'Lessons for America'),
                ('Shoe Dog', 'Phil Knight', 'A memoir by Nike creator'),
            ],
            'classic-literature': [
                ('Pride and Prejudice', 'Jane Austen', 'Love and social standing'),
                ('1984', 'George Orwell', 'Dystopian masterpiece'),
                ('To Kill a Mockingbird', 'Harper Lee', 'Racial injustice'),
                ('The Great Gatsby', 'F. Scott Fitzgerald', 'American Dream corruption'),
                ('One Hundred Years of Solitude', 'Gabriel Garcia Marquez', 'Magical realist epic'),
                ('Crime and Punishment', 'Fyodor Dostoevsky', 'Psychological morality'),
                ('The Catcher in the Rye', 'J.D. Salinger', 'Teenage alienation'),
                ('Wuthering Heights', 'Emily Bronte', 'Passion and revenge'),
                ('Great Expectations', 'Charles Dickens', 'Ambition and self-improvement'),
                ('Anna Karenina', 'Leo Tolstoy', 'Love and society'),
                ('Jane Eyre', 'Charlotte Bronte', 'Independent womans journey'),
                ('The Picture of Dorian Gray', 'Oscar Wilde', 'Beauty and corruption'),
                ('Moby Dick', 'Herman Melville', 'Hunt for white whale'),
                ('Don Quixote', 'Miguel de Cervantes', 'Adventures of a knight'),
                ('Les Miserables', 'Victor Hugo', 'Justice and redemption'),
                ('War and Peace', 'Leo Tolstoy', 'Napoleonic Wars epic'),
                ('The Brothers Karamazov', 'Fyodor Dostoevsky', 'Faith and morality'),
                ('Frankenstein', 'Mary Shelley', 'Dangers of playing God'),
                ('Dracula', 'Bram Stoker', 'Original vampire tale'),
                ('The Count of Monte Cristo', 'Alexandre Dumas', 'Betrayal and revenge'),
                ('A Tale of Two Cities', 'Charles Dickens', 'French Revolution'),
                ('Oliver Twist', 'Charles Dickens', 'Story of an orphan'),
                ('The Scarlet Letter', 'Nathaniel Hawthorne', 'Sin and redemption'),
                ('Madame Bovary', 'Gustave Flaubert', 'Dreams and disillusionment'),
                ('Huckleberry Finn', 'Mark Twain', 'Coming of age on the river'),
            ],
            'science-technology': [
                ('A Brief History of Time', 'Stephen Hawking', 'Understanding the universe'),
                ('The Origin of Species', 'Charles Darwin', 'Evolution by natural selection'),
                ('Sapiens', 'Yuval Noah Harari', 'Brief history of humankind'),
                ('The Selfish Gene', 'Richard Dawkins', 'Gene-centered evolution'),
                ('Cosmos', 'Carl Sagan', 'Personal voyage through space'),
                ('The Gene', 'Siddhartha Mukherjee', 'Intimate history of genetics'),
                ('Silent Spring', 'Rachel Carson', 'Environmental movement begins'),
                ('The Structure of Scientific Revolutions', 'Thomas Kuhn', 'How science progresses'),
                ('The Elegant Universe', 'Brian Greene', 'String theory explained'),
                ('Astrophysics for People in a Hurry', 'Neil deGrasse Tyson', 'Universe for busy people'),
                ('The Code Book', 'Simon Singh', 'Science of secrecy'),
                ('Surely Youre Joking Mr Feynman', 'Richard Feynman', 'Curious character adventures'),
                ('The Immortal Life of Henrietta Lacks', 'Rebecca Skloot', 'HeLa cells and ethics'),
                ('The Innovators', 'Walter Isaacson', 'Digital revolution'),
                ('Steve Jobs', 'Walter Isaacson', 'Life of Apple founder'),
                ('Elon Musk', 'Ashlee Vance', 'Tesla SpaceX future'),
                ('The Future of Humanity', 'Michio Kaku', 'Our destiny in universe'),
                ('Life 3.0', 'Max Tegmark', 'Being human in age of AI'),
                ('Homo Deus', 'Yuval Noah Harari', 'Brief history of tomorrow'),
                ('21 Lessons for 21st Century', 'Yuval Noah Harari', 'What we need to know'),
                ('The Emperor of All Maladies', 'Siddhartha Mukherjee', 'Biography of cancer'),
                ('The Double Helix', 'James Watson', 'Discovery of DNA'),
                ('Chaos', 'James Gleick', 'Making a new science'),
                ('The Singularity Is Near', 'Ray Kurzweil', 'Transcending biology'),
                ('Code', 'Charles Petzold', 'Hidden language of computers'),
            ],
            'philosophy': [
                ('Meditations', 'Marcus Aurelius', 'Stoic philosophy reflections'),
                ('The Republic', 'Plato', 'Justice and ideal state'),
                ('Nicomachean Ethics', 'Aristotle', 'Pursuit of happiness'),
                ('Beyond Good and Evil', 'Friedrich Nietzsche', 'Challenging morality'),
                ('Being and Time', 'Martin Heidegger', 'Meaning of being'),
                ('The Art of War', 'Sun Tzu', 'Ancient military strategy'),
                ('Thus Spoke Zarathustra', 'Friedrich Nietzsche', 'The Ubermensch'),
                ('The Prince', 'Niccolo Machiavelli', 'Political power strategy'),
                ('Critique of Pure Reason', 'Immanuel Kant', 'Limits of knowledge'),
                ('The Social Contract', 'Jean-Jacques Rousseau', 'Political philosophy'),
                ('Utilitarianism', 'John Stuart Mill', 'Greatest good principle'),
                ('The Stranger', 'Albert Camus', 'Absurdism existentialism'),
                ('Being and Nothingness', 'Jean-Paul Sartre', 'Existentialist philosophy'),
                ('The Tao Te Ching', 'Lao Tzu', 'Way of the Tao'),
                ('The Book of Five Rings', 'Miyamoto Musashi', 'Strategy and warrior way'),
                ('Mans Search for Meaning', 'Viktor Frankl', 'Purpose through suffering'),
                ('The Alchemist', 'Paulo Coelho', 'Following personal legend'),
                ('Siddhartha', 'Hermann Hesse', 'Journey to enlightenment'),
                ('Letters from a Stoic', 'Seneca', 'Practical Stoic wisdom'),
                ('The Enchiridion', 'Epictetus', 'Manual for living'),
                ('On the Shortness of Life', 'Seneca', 'Time and how we spend it'),
                ('Walden', 'Henry David Thoreau', 'Simple living in nature'),
                ('The Myth of Sisyphus', 'Albert Camus', 'Absurdity and meaning'),
                ('Fear and Trembling', 'Soren Kierkegaard', 'Faith and individual'),
                ('The Consolation of Philosophy', 'Boethius', 'Finding meaning in adversity'),
            ],
            'history': [
                ('Guns Germs and Steel', 'Jared Diamond', 'Fates of human societies'),
                ('A Peoples History of the US', 'Howard Zinn', 'History from below'),
                ('Rise and Fall of Third Reich', 'William Shirer', 'Nazi Germany'),
                ('SPQR', 'Mary Beard', 'History of ancient Rome'),
                ('The Diary of Anne Frank', 'Anne Frank', 'Life during Holocaust'),
                ('Team of Rivals', 'Doris Kearns Goodwin', 'Lincolns political genius'),
                ('The Wright Brothers', 'David McCullough', 'Story of aviation'),
                ('1776', 'David McCullough', 'American Revolution'),
                ('Alexander Hamilton', 'Ron Chernow', 'The founding father'),
                ('Unbroken', 'Laura Hillenbrand', 'WWII survival story'),
                ('Genghis Khan', 'Jack Weatherford', 'Mongol Empire'),
                ('Salt A World History', 'Mark Kurlansky', 'Mineral that shaped civilization'),
                ('Devil in the White City', 'Erik Larson', 'Murder and 1893 Worlds Fair'),
                ('Dead Wake', 'Erik Larson', 'Sinking of Lusitania'),
                ('In the Garden of Beasts', 'Erik Larson', 'Berlin 1933-1934'),
                ('The Splendid and the Vile', 'Erik Larson', 'Churchill and Blitz'),
                ('Catherine the Great', 'Robert Massie', 'Portrait of a woman'),
                ('Peter the Great', 'Robert Massie', 'His life and world'),
                ('The Silk Roads', 'Peter Frankopan', 'New history of world'),
                ('A Short History of Nearly Everything', 'Bill Bryson', 'Science made accessible'),
                ('The History of Ancient World', 'Susan Wise Bauer', 'From earliest accounts'),
                ('The Story of Civilization', 'Will Durant', 'Cultural heritage'),
                ('The Lessons of History', 'Will Durant', 'What history teaches'),
                ('Rubicon', 'Tom Holland', 'Last years of Roman Republic'),
                ('Empire of the Summer Moon', 'S.C. Gwynne', 'Comanches and Texas'),
            ],
            'fiction': [
                ('The Lord of the Rings', 'J.R.R. Tolkien', 'Epic fantasy masterpiece'),
                ('Harry Potter', 'J.K. Rowling', 'The boy who lived'),
                ('The Hobbit', 'J.R.R. Tolkien', 'There and back again'),
                ('Dune', 'Frank Herbert', 'Science fiction epic'),
                ('The Hunger Games', 'Suzanne Collins', 'Dystopian survival'),
                ('Game of Thrones', 'George R.R. Martin', 'Song of Ice and Fire'),
                ('The Name of the Wind', 'Patrick Rothfuss', 'Kingkiller Chronicle'),
                ('Enders Game', 'Orson Scott Card', 'Child soldiers in space'),
                ('The Martian', 'Andy Weir', 'Survival on Mars'),
                ('Ready Player One', 'Ernest Cline', 'Virtual reality adventure'),
                ('The Da Vinci Code', 'Dan Brown', 'Mystery and conspiracy'),
                ('Angels and Demons', 'Dan Brown', 'The Illuminati'),
                ('Girl with Dragon Tattoo', 'Stieg Larsson', 'Scandinavian noir'),
                ('Gone Girl', 'Gillian Flynn', 'Marriage gone wrong'),
                ('The Kite Runner', 'Khaled Hosseini', 'Friendship in Afghanistan'),
                ('Life of Pi', 'Yann Martel', 'Survival at sea'),
                ('The Book Thief', 'Markus Zusak', 'Death narrates WWII'),
                ('The Night Circus', 'Erin Morgenstern', 'Magical competition'),
                ('Cloud Atlas', 'David Mitchell', 'Six interconnected stories'),
                ('Station Eleven', 'Emily St. John Mandel', 'Post-apocalyptic fiction'),
                ('Project Hail Mary', 'Andy Weir', 'Astronaut saves Earth'),
                ('The Silent Patient', 'Alex Michaelides', 'Psychological thriller'),
                ('Where Crawdads Sing', 'Delia Owens', 'Mystery in the marsh'),
                ('Circe', 'Madeline Miller', 'Greek mythology witch'),
                ('Song of Achilles', 'Madeline Miller', 'Trojan War retold'),
            ],
            'health-wellness': [
                ('Why We Sleep', 'Matthew Walker', 'Power of sleep'),
                ('The Body Keeps the Score', 'Bessel van der Kolk', 'Healing trauma'),
                ('How Not to Die', 'Michael Greger', 'Foods that prevent disease'),
                ('In Defense of Food', 'Michael Pollan', 'Eaters manifesto'),
                ('The Omnivores Dilemma', 'Michael Pollan', 'Natural history of four meals'),
                ('Born to Run', 'Christopher McDougall', 'Hidden tribe super athletes'),
                ('Breath', 'James Nestor', 'New science of lost art'),
                ('Spark', 'John Ratey', 'Exercise and the brain'),
                ('The China Study', 'T. Colin Campbell', 'Nutrition and health'),
                ('Brain Food', 'Lisa Mosconi', 'Eating for cognitive power'),
                ('Lifespan', 'David Sinclair', 'Why we age'),
                ('Grain Brain', 'David Perlmutter', 'Truth about carbs'),
                ('The Whole30', 'Melissa Hartwig', '30-day health guide'),
                ('It Starts with Food', 'Dallas Hartwig', 'Food and health program'),
                ('The Plant Paradox', 'Steven Gundry', 'Hidden dangers in healthy foods'),
                ('The Bulletproof Diet', 'Dave Asprey', 'Lose up to a pound a day'),
                ('Tools of Titans', 'Tim Ferriss', 'Tactics routines habits'),
                ('The 4-Hour Body', 'Tim Ferriss', 'Guide to rapid fat-loss'),
                ('Mindfulness in Plain English', 'Bhante Gunaratana', 'Meditation practice'),
                ('Headspace Guide to Meditation', 'Andy Puddicombe', 'Mindfulness guide'),
                ('Atomic Habits', 'James Clear', 'Tiny changes big results'),
                ('The Sleep Revolution', 'Arianna Huffington', 'Transforming your life'),
                ('Intuitive Eating', 'Evelyn Tribole', 'Revolutionary anti-diet approach'),
                ('Food Rules', 'Michael Pollan', 'Eaters manual'),
                ('The Blue Zones', 'Dan Buettner', 'Lessons for living longer'),
            ],
            'psychology': [
                ('Influence', 'Robert Cialdini', 'Psychology of persuasion'),
                ('Predictably Irrational', 'Dan Ariely', 'Hidden forces shaping decisions'),
                ('Man Who Mistook Wife for Hat', 'Oliver Sacks', 'Neurological case studies'),
                ('Flow', 'Mihaly Csikszentmihalyi', 'Psychology of optimal experience'),
                ('Stumbling on Happiness', 'Daniel Gilbert', 'Why we misjudge happiness'),
                ('The Paradox of Choice', 'Barry Schwartz', 'Why more is less'),
                ('Quiet', 'Susan Cain', 'Power of introverts'),
                ('The Happiness Hypothesis', 'Jonathan Haidt', 'Modern truth ancient wisdom'),
                ('Drive', 'Daniel Pink', 'What motivates us'),
                ('The Willpower Instinct', 'Kelly McGonigal', 'How self-control works'),
                ('Blink', 'Malcolm Gladwell', 'Thinking without thinking'),
                ('The Tipping Point', 'Malcolm Gladwell', 'Little things big difference'),
                ('Talking to Strangers', 'Malcolm Gladwell', 'What we should know'),
                ('The Social Animal', 'David Brooks', 'Hidden sources of love'),
                ('Attached', 'Amir Levine', 'Science of adult attachment'),
                ('The 5 Love Languages', 'Gary Chapman', 'Express heartfelt commitment'),
                ('Games People Play', 'Eric Berne', 'Psychology of relationships'),
                ('The Gift of Fear', 'Gavin de Becker', 'Survival signals'),
                ('The Power of Vulnerability', 'Brene Brown', 'Courage and connection'),
                ('Daring Greatly', 'Brene Brown', 'Courage transforms lives'),
                ('Rising Strong', 'Brene Brown', 'How to get back up'),
                ('Gifts of Imperfection', 'Brene Brown', 'Letting go of who you should be'),
                ('Thinking Fast and Slow', 'Daniel Kahneman', 'Two systems of thinking'),
                ('The Psychopath Test', 'Jon Ronson', 'Journey through madness industry'),
                ('Emotions Revealed', 'Paul Ekman', 'Recognizing faces and feelings'),
            ],
            'educational-materials': [
                ('A Short History of Nearly Everything', 'Bill Bryson', 'Science made accessible'),
                ('The Elements of Style', 'Strunk and White', 'Classic writing guide'),
                ('On Writing', 'Stephen King', 'Memoir of the craft'),
                ('Bird by Bird', 'Anne Lamott', 'Instructions on writing and life'),
                ('The Sense of Style', 'Steven Pinker', 'Thinking persons writing guide'),
                ('Made to Stick', 'Chip Heath', 'Why ideas survive'),
                ('The Art of Learning', 'Josh Waitzkin', 'Journey to excellence'),
                ('Peak', 'Anders Ericsson', 'Science of expertise'),
                ('Moonwalking with Einstein', 'Joshua Foer', 'Art of remembering'),
                ('Make It Stick', 'Peter Brown', 'Science of successful learning'),
                ('A Mind for Numbers', 'Barbara Oakley', 'Excel at math and science'),
                ('Learning How to Learn', 'Barbara Oakley', 'Powerful mental tools'),
                ('The Talent Code', 'Daniel Coyle', 'Greatness is grown'),
                ('Ultralearning', 'Scott Young', 'Master hard skills fast'),
                ('Range', 'David Epstein', 'Why generalists triumph'),
                ('The First 20 Hours', 'Josh Kaufman', 'Learn anything fast'),
                ('Mastery', 'Robert Greene', 'Keys to success and fulfillment'),
                ('So Good They Cant Ignore You', 'Cal Newport', 'Skills trump passion'),
                ('The Personal MBA', 'Josh Kaufman', 'Master the art of business'),
                ('How to Read a Book', 'Mortimer Adler', 'Classic reading guide'),
                ('The Well-Educated Mind', 'Susan Wise Bauer', 'Guide to classical education'),
                ('How to Take Smart Notes', 'Sonke Ahrens', 'One simple technique'),
                ('Building a Second Brain', 'Tiago Forte', 'Saving and organizing ideas'),
                ('Show Your Work', 'Austin Kleon', 'Share your creativity'),
                ('Steal Like an Artist', 'Austin Kleon', 'Creative advice'),
            ],
        }
    
    def create_extra_articles(self, admin_user, categories, tags, difficulties, current_count):
        extra_template = '''# {title}

## Introduction

Welcome to this comprehensive guide on {topic}. This article provides actionable insights and practical strategies.

## Why This Matters

Understanding {topic} is crucial today. This guide helps you:

- Gain foundational understanding
- Learn practical techniques
- Avoid common mistakes
- Achieve better results

## Key Concepts

### Foundation

Every journey starts with basics. The foundation of {topic} rests on key principles proven effective over time.

### Strategy

Having clear strategy is essential. Consider these approaches:

1. **Goal Setting**: Define success
2. **Planning**: Create a roadmap
3. **Execution**: Take consistent action
4. **Review**: Assess and adjust

### Implementation

Ideas without action are worthless. Implementation tips:

- Start small
- Be consistent
- Track progress
- Stay patient

## Practical Applications

Incorporate these principles into daily routine. Start with small changes and build momentum.

## Common Mistakes

1. Skipping fundamentals
2. Expecting quick results
3. Going it alone
4. Perfectionism
5. Inconsistency

## Summary

{topic} is valuable area of focus. Start with basics, be consistent, stay patient, keep learning.

---

*This guide provides overview of {topic}. Continue exploring through practice.*'''

        extra_topics = [
            ('How to Master', ['Time Management', 'Public Speaking', 'Negotiation', 'Critical Thinking', 'Problem Solving', 'Decision Making', 'Emotional Intelligence', 'Communication Skills', 'Leadership Skills', 'Creativity', 'Focus', 'Memory', 'Speed Reading', 'Note Taking', 'Research Skills']),
            ('The Science of', ['Happiness', 'Success', 'Learning', 'Memory', 'Motivation', 'Habits', 'Sleep', 'Exercise', 'Nutrition', 'Relationships', 'Creativity', 'Productivity', 'Willpower', 'Emotions', 'Behavior']),
            ('Guide to', ['Financial Freedom', 'Career Success', 'Personal Branding', 'Networking', 'Entrepreneurship', 'Investing', 'Real Estate', 'Stock Market', 'Cryptocurrency', 'Passive Income', 'Side Hustles', 'Freelancing', 'Remote Work', 'Job Hunting', 'Salary Negotiation']),
            ('Understanding', ['Human Behavior', 'Psychology Basics', 'Economics 101', 'Philosophy Intro', 'World History', 'Modern Science', 'Technology Trends', 'Art History', 'Music Theory', 'Literature Analysis', 'Politics', 'Sociology', 'Anthropology', 'Biology', 'Physics']),
            ('Secrets of', ['Successful People', 'Great Leaders', 'Top Athletes', 'Entrepreneurs', 'Scientists', 'Artists', 'Writers', 'Musicians', 'Innovators', 'Visionaries', 'Billionaires', 'CEOs', 'Inventors', 'Philosophers', 'Coaches']),
            ('Principles of', ['Design Thinking', 'Software Engineering', 'Digital Marketing', 'Sales Mastery', 'Team Management', 'Business Strategy', 'Product Innovation', 'Quality Excellence', 'Customer Service', 'Brand Building', 'Agile', 'Lean', 'Six Sigma', 'Project Management', 'Risk Management']),
            ('Introduction to', ['Machine Learning', 'Artificial Intelligence', 'Data Science', 'Programming Basics', 'Web Development', 'Mobile Apps', 'Cloud Computing', 'Cybersecurity', 'Blockchain', 'Internet of Things', 'Python', 'JavaScript', 'SQL', 'APIs', 'Databases']),
            ('The Art of', ['Clear Thinking', 'Mindful Living', 'Loving Relationships', 'Productive Work', 'Creative Expression', 'Effective Leading', 'Great Teaching', 'Deep Learning', 'Powerful Writing', 'Public Speaking', 'Persuasion', 'Storytelling', 'Listening', 'Feedback', 'Mentoring']),
            ('Essential', ['Life Skills', 'Career Skills', 'Tech Skills', 'Soft Skills', 'Hard Skills', 'Social Skills', 'Financial Skills', 'Leadership Skills', 'Communication Skills', 'Problem Solving Skills', 'Analytical Skills', 'Creative Skills', 'Management Skills', 'Organizational Skills', 'Interpersonal Skills']),
            ('Complete Course on', ['Personal Finance', 'Stock Investing', 'Real Estate', 'Business Management', 'Marketing Strategy', 'Sales Techniques', 'Leadership Development', 'Team Building', 'Conflict Resolution', 'Time Management', 'Stress Management', 'Goal Setting', 'Decision Making', 'Strategic Planning', 'Change Management']),
        ]
        
        themes = ['Beginner Guide', 'Advanced Strategies', 'Pro Tips', 'Quick Start', 'Deep Dive', 'Masterclass', 'Fundamentals', 'Best Practices', 'Complete Guide', 'Expert Tips', 'Essential Guide', 'Comprehensive Overview']
        subjects = [
            'Python Programming', 'JavaScript Basics', 'Data Analysis', 'Web Design', 'Mobile Development',
            'Project Management', 'Team Leadership', 'Remote Work', 'Freelancing', 'Consulting',
            'Personal Finance', 'Investment Basics', 'Retirement Planning', 'Budget Management', 'Wealth Building',
            'Content Creation', 'Social Media', 'Email Marketing', 'SEO Basics', 'Digital Advertising',
            'Fitness Training', 'Nutrition Planning', 'Weight Loss', 'Muscle Building', 'Yoga Practice',
            'Meditation', 'Stress Relief', 'Sleep Improvement', 'Energy Management', 'Focus Training',
            'Public Speaking', 'Presentation Skills', 'Negotiation', 'Conflict Resolution', 'Team Collaboration',
            'Creative Writing', 'Copywriting', 'Technical Writing', 'Blog Writing', 'Content Strategy',
            'Photography', 'Video Editing', 'Graphic Design', 'UI UX Design', 'Product Design',
            'Database Management', 'Cloud Services', 'DevOps', 'System Administration', 'Network Security',
        ]
        
        count = current_count
        
        # Create from extra_topics
        for prefix, topics in extra_topics:
            for topic in topics:
                if count >= 1050:
                    return
                title = f"{prefix} {topic}"
                slug = self.make_slug(title)
                if Article.objects.filter(slug=slug).exists():
                    continue
                content = extra_template.format(title=title, topic=topic)
                article = Article.objects.create(
                    title=title, slug=slug, author=admin_user, content=content,
                    summary=f"Comprehensive guide to {topic.lower()}.",
                    category=random.choice(categories), difficulty=random.choice(difficulties),
                    estimated_read_time=random.randint(5, 15), is_published=True, is_featured=random.random() < 0.05,
                )
                article.tags.set(random.sample(tags, k=min(3, len(tags))))
                count += 1
        
        # Create from themes and subjects
        for theme in themes:
            for subject in subjects:
                if count >= 1050:
                    return
                title = f"{subject}: {theme}"
                slug = self.make_slug(title)
                if Article.objects.filter(slug=slug).exists():
                    continue
                content = extra_template.format(title=title, topic=subject)
                article = Article.objects.create(
                    title=title, slug=slug, author=admin_user, content=content,
                    summary=f"{theme} for {subject}.",
                    category=random.choice(categories), difficulty=random.choice(difficulties),
                    estimated_read_time=random.randint(5, 20), is_published=True, is_featured=random.random() < 0.03,
                )
                article.tags.set(random.sample(tags, k=min(3, len(tags))))
                count += 1
        
        # Create even more with different patterns
        more_prefixes = ['Learn', 'Discover', 'Explore', 'Master', 'Unlock', 'Build', 'Develop', 'Improve', 'Enhance', 'Transform']
        more_topics = [
            'Your Mindset', 'Your Skills', 'Your Career', 'Your Finances', 'Your Health',
            'Your Relationships', 'Your Productivity', 'Your Creativity', 'Your Leadership', 'Your Communication',
            'Critical Thinking', 'Analytical Skills', 'Strategic Thinking', 'Problem Solving', 'Decision Making',
            'Emotional Intelligence', 'Social Intelligence', 'Financial Intelligence', 'Business Intelligence', 'Cultural Intelligence',
        ]
        
        for prefix in more_prefixes:
            for topic in more_topics:
                if count >= 1050:
                    return
                title = f"{prefix} {topic}"
                slug = self.make_slug(title)
                if Article.objects.filter(slug=slug).exists():
                    continue
                content = extra_template.format(title=title, topic=topic)
                article = Article.objects.create(
                    title=title, slug=slug, author=admin_user, content=content,
                    summary=f"How to {prefix.lower()} {topic.lower()}.",
                    category=random.choice(categories), difficulty=random.choice(difficulties),
                    estimated_read_time=random.randint(5, 15), is_published=True, is_featured=random.random() < 0.02,
                )
                article.tags.set(random.sample(tags, k=min(3, len(tags))))
                count += 1
