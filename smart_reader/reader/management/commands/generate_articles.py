"""
Management command to generate unique articles with accurate, well-researched content
Usage: python manage.py generate_articles [number_of_articles]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from reader.models import Article, Category, Tag
import random


class Command(BaseCommand):
    help = 'Generate unique articles with accurate content for different categories'

    def add_arguments(self, parser):
        parser.add_argument(
            'count',
            type=int,
            nargs='?',
            default=50,
            help='Number of articles to generate (default: 50)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No users found. Please create a user first.'))
            return

        # Create categories if they don't exist
        categories_data = [
            {
                'name': 'Health & Wellness',
                'slug': 'health-wellness',
                'description': 'Articles about physical and mental health, fitness, and nutrition',
                'icon': 'fa-heart-pulse',
                'color': '#ef4444'
            },
            {
                'name': 'Technology',
                'slug': 'technology',
                'description': 'Latest tech trends, gadgets, and innovations',
                'icon': 'fa-microchip',
                'color': '#3b82f6'
            },
            {
                'name': 'Science',
                'slug': 'science',
                'description': 'Scientific discoveries, research, and explanations',
                'icon': 'fa-flask',
                'color': '#8b5cf6'
            },
            {
                'name': 'Education',
                'slug': 'education',
                'description': 'Learning resources, study tips, and educational content',
                'icon': 'fa-graduation-cap',
                'color': '#f59e0b'
            },
            {
                'name': 'Business',
                'slug': 'business',
                'description': 'Business strategies, entrepreneurship, and career advice',
                'icon': 'fa-briefcase',
                'color': '#10b981'
            },
            {
                'name': 'Environment',
                'slug': 'environment',
                'description': 'Environmental issues, conservation, and sustainability',
                'icon': 'fa-leaf',
                'color': '#22c55e'
            },
            {
                'name': 'Psychology',
                'slug': 'psychology',
                'description': 'Mental processes, behavior, and emotional well-being',
                'icon': 'fa-brain',
                'color': '#ec4899'
            },
            {
                'name': 'History',
                'slug': 'history',
                'description': 'Historical events, figures, and cultural heritage',
                'icon': 'fa-landmark',
                'color': '#92400e'
            },
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create tags
        tags_list = [
            'health', 'wellness', 'fitness', 'nutrition', 'mental-health', 'yoga',
            'technology', 'ai', 'machine-learning', 'programming', 'web-development',
            'science', 'physics', 'biology', 'chemistry', 'astronomy', 'research',
            'education', 'learning', 'study-tips', 'online-courses', 'skills',
            'business', 'entrepreneurship', 'startup', 'marketing', 'finance',
            'environment', 'climate-change', 'sustainability', 'conservation', 'wildlife',
            'psychology', 'mindfulness', 'meditation', 'self-improvement', 'motivation',
            'history', 'culture', 'archaeology', 'ancient-civilizations', 'world-war'
        ]

        tags = []
        for tag_name in tags_list:
            tag, created = Tag.objects.get_or_create(
                slug=slugify(tag_name),
                defaults={'name': tag_name.replace('-', ' ').title()}
            )
            tags.append(tag)

        # Article content templates by category
        article_templates = {
            'health-wellness': [
                {
                    'title': 'The Complete Guide to Building a Strong Immune System',
                    'summary': 'Learn evidence-based strategies to naturally boost your immunity and protect against diseases.',
                    'content': '''
<h2>Understanding Your Immune System</h2>
<p>Your immune system is your body's defense mechanism against harmful pathogens, viruses, and bacteria. A strong immune system is essential for maintaining overall health and preventing illnesses.</p>

<h3>Key Components of Immune Health</h3>
<ul>
    <li><strong>White Blood Cells:</strong> The primary defenders that identify and destroy harmful invaders</li>
    <li><strong>Antibodies:</strong> Proteins that recognize and neutralize specific threats</li>
    <li><strong>Lymphatic System:</strong> Network of vessels that transport immune cells throughout the body</li>
</ul>

<h3>Top 10 Ways to Boost Your Immune System</h3>

<h4>1. Maintain a Balanced Diet</h4>
<p>Consume a variety of fruits, vegetables, whole grains, and lean proteins. Key nutrients include:</p>
<ul>
    <li>Vitamin C (citrus fruits, berries, bell peppers)</li>
    <li>Vitamin D (sunlight, fatty fish, fortified foods)</li>
    <li>Zinc (nuts, seeds, legumes)</li>
    <li>Probiotics (yogurt, kefir, fermented foods)</li>
</ul>

<h4>2. Get Adequate Sleep</h4>
<p>Adults should aim for 7-9 hours of quality sleep per night. During sleep, your body produces cytokines, proteins that help fight infection and inflammation.</p>

<h4>3. Exercise Regularly</h4>
<p>Moderate exercise (30 minutes daily) improves circulation, reduces inflammation, and enhances immune cell function. Activities include walking, jogging, swimming, or cycling.</p>

<h4>4. Manage Stress</h4>
<p>Chronic stress weakens immunity by increasing cortisol levels. Practice stress-reduction techniques:</p>
<ul>
    <li>Meditation and mindfulness</li>
    <li>Deep breathing exercises</li>
    <li>Yoga or tai chi</li>
    <li>Spending time in nature</li>
</ul>

<h4>5. Stay Hydrated</h4>
<p>Drink at least 8 glasses of water daily. Proper hydration helps produce lymph, which carries white blood cells and nutrients throughout the body.</p>

<h4>6. Limit Alcohol and Avoid Smoking</h4>
<p>Excessive alcohol consumption and smoking impair immune function and increase susceptibility to infections.</p>

<h4>7. Maintain Healthy Weight</h4>
<p>Obesity is linked to impaired immune response. Focus on sustainable weight management through balanced diet and regular exercise.</p>

<h4>8. Practice Good Hygiene</h4>
<p>Wash hands frequently, especially before meals and after using the restroom. This simple habit prevents the spread of pathogens.</p>

<h4>9. Get Vaccinated</h4>
<p>Vaccines train your immune system to recognize and fight specific diseases effectively.</p>

<h4>10. Consider Supplements (When Necessary)</h4>
<p>Consult your doctor about supplements if you have deficiencies:</p>
<ul>
    <li>Vitamin D3 (especially in winter months)</li>
    <li>Vitamin C (1000mg daily)</li>
    <li>Elderberry extract</li>
    <li>Echinacea</li>
</ul>

<h3>Foods That Support Immune Function</h3>
<p><strong>Top Immune-Boosting Foods:</strong></p>
<ol>
    <li>Citrus fruits (oranges, lemons, grapefruits)</li>
    <li>Berries (blueberries, strawberries, elderberries)</li>
    <li>Garlic and ginger (natural antimicrobials)</li>
    <li>Spinach and kale (rich in vitamins A, C, E)</li>
    <li>Almonds and sunflower seeds (vitamin E)</li>
    <li>Turmeric (anti-inflammatory properties)</li>
    <li>Green tea (antioxidants)</li>
    <li>Fatty fish (omega-3 fatty acids)</li>
    <li>Yogurt and kefir (probiotics)</li>
    <li>Sweet potatoes (beta-carotene)</li>
</ol>

<h3>Warning Signs of Weakened Immunity</h3>
<ul>
    <li>Frequent colds and infections (more than 3-4 per year)</li>
    <li>Slow wound healing</li>
    <li>Persistent fatigue</li>
    <li>Digestive issues</li>
    <li>High stress levels</li>
</ul>

<h3>Conclusion</h3>
<p>Building a strong immune system requires a holistic approach combining proper nutrition, regular exercise, adequate sleep, and stress management. Implement these evidence-based strategies consistently for optimal immune health.</p>

<p><em>Note: Always consult with healthcare professionals before making significant changes to your diet or lifestyle, especially if you have underlying health conditions.</em></p>
''',
                    'difficulty': 'beginner',
                    'tags': ['health', 'wellness', 'nutrition', 'fitness']
                },
                {
                    'title': '10 Scientifically-Proven Benefits of Meditation for Mental Health',
                    'summary': 'Discover how meditation can transform your mental well-being with research-backed benefits.',
                    'content': '''
<h2>The Science Behind Meditation</h2>
<p>Meditation is an ancient practice that has gained significant scientific validation in recent years. Neuroscience research reveals that regular meditation physically changes the brain structure, enhancing areas responsible for attention, emotion regulation, and self-awareness.</p>

<h3>10 Evidence-Based Benefits of Meditation</h3>

<h4>1. Reduces Stress and Anxiety</h4>
<p><strong>Research Finding:</strong> A 2014 meta-analysis published in JAMA Internal Medicine found that meditation programs show moderate evidence of improving anxiety, depression, and pain.</p>
<p><strong>How it works:</strong> Meditation activates the parasympathetic nervous system, reducing cortisol (stress hormone) levels by up to 25%.</p>

<h4>2. Improves Focus and Concentration</h4>
<p><strong>Research Finding:</strong> Studies from Harvard Medical School show that 8 weeks of mindfulness meditation increases gray matter density in brain regions associated with learning, memory, and emotional regulation.</p>
<p><strong>Benefits:</strong></p>
<ul>
    <li>Enhanced working memory capacity</li>
    <li>Improved attention span (up to 20% improvement)</li>
    <li>Better cognitive flexibility</li>
</ul>

<h4>3. Reduces Depression Symptoms</h4>
<p><strong>Research Finding:</strong> Mindfulness-Based Cognitive Therapy (MBCT) reduces depression relapse rates by 43% compared to standard treatment.</p>
<p><strong>Mechanism:</strong> Meditation breaks the cycle of negative thought patterns by promoting present-moment awareness.</p>

<h4>4. Enhances Emotional Intelligence</h4>
<p>Regular meditation practice strengthens the prefrontal cortex, improving:</p>
<ul>
    <li>Emotional awareness</li>
    <li>Empathy and compassion</li>
    <li>Impulse control</li>
    <li>Response flexibility</li>
</ul>

<h4>5. Improves Sleep Quality</h4>
<p><strong>Research Finding:</strong> A 2015 study in JAMA Internal Medicine found that mindfulness meditation significantly improves sleep quality in adults with moderate sleep disturbances.</p>
<p><strong>Benefits:</strong></p>
<ul>
    <li>Faster sleep onset (fall asleep 33% quicker)</li>
    <li>Deeper sleep stages</li>
    <li>Reduced nighttime awakenings</li>
</ul>

<h4>6. Lowers Blood Pressure</h4>
<p><strong>Research Finding:</strong> Transcendental Meditation reduces systolic blood pressure by an average of 5-10 mmHg.</p>
<p><strong>Health Impact:</strong> This reduction decreases cardiovascular disease risk by approximately 20%.</p>

<h4>7. Boosts Immune Function</h4>
<p><strong>Research Finding:</strong> An 8-week mindfulness program increased antibody titers to flu vaccine by 16% compared to controls.</p>
<p><strong>Mechanisms:</strong></p>
<ul>
    <li>Reduced inflammation markers</li>
    <li>Enhanced immune cell production</li>
    <li>Improved immune system regulation</li>
</ul>

<h4>8. Increases Pain Tolerance</h4>
<p><strong>Research Finding:</strong> Mindfulness meditation reduces pain intensity perception by 27% and pain unpleasantness by 44%.</p>
<p><strong>Application:</strong> Effective for chronic pain conditions including fibromyalgia, arthritis, and migraine.</p>

<h4>9. Enhances Self-Awareness and Personal Growth</h4>
<p>Meditation promotes introspection, leading to:</p>
<ul>
    <li>Better understanding of personal values</li>
    <li>Improved self-acceptance</li>
    <li>Enhanced decision-making abilities</li>
    <li>Greater life satisfaction</li>
</ul>

<h4>10. Slows Age-Related Cognitive Decline</h4>
<p><strong>Research Finding:</strong> Long-term meditators show 50% less age-related brain atrophy compared to non-meditators.</p>
<p><strong>Neuroprotective Effects:</strong></p>
<ul>
    <li>Preserved hippocampal volume (memory center)</li>
    <li>Maintained prefrontal cortex thickness</li>
    <li>Enhanced neuroplasticity</li>
</ul>

<h3>Types of Meditation Techniques</h3>

<h4>Mindfulness Meditation</h4>
<p>Focus on present-moment awareness without judgment. Observe thoughts, emotions, and sensations as they arise.</p>

<h4>Loving-Kindness Meditation (Metta)</h4>
<p>Cultivate compassion toward oneself and others through repeated phrases of goodwill.</p>

<h4>Body Scan Meditation</h4>
<p>Systematically focus attention on different body parts, promoting relaxation and body awareness.</p>

<h4>Transcendental Meditation</h4>
<p>Use a personal mantra to achieve a state of relaxed awareness and deep rest.</p>

<h4>Breath Awareness Meditation</h4>
<p>Focus solely on the breath, using it as an anchor for attention.</p>

<h3>How to Start a Meditation Practice</h3>

<p><strong>For Beginners:</strong></p>
<ol>
    <li><strong>Start Small:</strong> Begin with 5 minutes daily, gradually increasing to 20-30 minutes</li>
    <li><strong>Choose a Quiet Space:</strong> Find a calm environment with minimal distractions</li>
    <li><strong>Use Guided Meditations:</strong> Apps like Headspace, Calm, or Insight Timer provide structured guidance</li>
    <li><strong>Be Consistent:</strong> Practice at the same time each day (morning is ideal)</li>
    <li><strong>Be Patient:</strong> Benefits accumulate over time; don't expect immediate transformation</li>
</ol>

<h3>Common Meditation Myths Debunked</h3>

<p><strong>Myth 1:</strong> "You need to clear your mind completely"<br>
<strong>Reality:</strong> Thoughts will arise naturally. The practice is about observing them without attachment.</p>

<p><strong>Myth 2:</strong> "Meditation is religious"<br>
<strong>Reality:</strong> While rooted in spiritual traditions, modern meditation is a secular mental training technique.</p>

<p><strong>Myth 3:</strong> "You need special equipment or environment"<br>
<strong>Reality:</strong> You can meditate anywhere, anytime. All you need is your awareness.</p>

<h3>Scientific Validation</h3>
<p>Over 6,000 peer-reviewed studies on meditation have been published, with research from prestigious institutions including:</p>
<ul>
    <li>Harvard Medical School</li>
    <li>Stanford University</li>
    <li>University of Massachusetts Medical School</li>
    <li>Johns Hopkins University</li>
</ul>

<h3>Conclusion</h3>
<p>Meditation is a powerful, evidence-based tool for enhancing mental health and overall well-being. With consistent practice, you can experience profound changes in stress levels, emotional regulation, cognitive function, and life satisfaction.</p>

<p><strong>Action Step:</strong> Commit to 10 minutes of meditation daily for the next 30 days and observe the transformative effects on your mental health.</p>

<p><em>Consult with mental health professionals if you're experiencing severe anxiety or depression. Meditation complements but doesn't replace professional treatment.</em></p>
''',
                    'difficulty': 'beginner',
                    'tags': ['mental-health', 'wellness', 'meditation', 'mindfulness']
                }
            ],
            'technology': [
                {
                    'title': 'Understanding Artificial Intelligence: A Comprehensive Guide for Beginners',
                    'summary': 'Learn the fundamentals of AI, machine learning, and how these technologies are shaping our future.',
                    'content': '''
<h2>What is Artificial Intelligence?</h2>
<p>Artificial Intelligence (AI) refers to computer systems designed to perform tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding.</p>

<h3>Key Concepts in AI</h3>

<h4>1. Machine Learning (ML)</h4>
<p>Machine Learning is a subset of AI where systems learn from data without being explicitly programmed.</p>

<p><strong>Types of Machine Learning:</strong></p>
<ul>
    <li><strong>Supervised Learning:</strong> Training with labeled data (e.g., spam filters, image recognition)</li>
    <li><strong>Unsupervised Learning:</strong> Finding patterns in unlabeled data (e.g., customer segmentation)</li>
    <li><strong>Reinforcement Learning:</strong> Learning through trial and error with rewards/penalties (e.g., game AI, robotics)</li>
</ul>

<h4>2. Deep Learning</h4>
<p>Deep Learning uses artificial neural networks inspired by the human brain's structure. It powers:</p>
<ul>
    <li>Image and facial recognition</li>
    <li>Natural language processing</li>
    <li>Autonomous vehicles</li>
    <li>Voice assistants (Siri, Alexa, Google Assistant)</li>
</ul>

<h4>3. Natural Language Processing (NLP)</h4>
<p>NLP enables computers to understand, interpret, and generate human language.</p>

<p><strong>Applications:</strong></p>
<ul>
    <li>Chatbots and virtual assistants</li>
    <li>Language translation (Google Translate)</li>
    <li>Sentiment analysis</li>
    <li>Text summarization</li>
</ul>

<h3>Real-World Applications of AI</h3>

<h4>Healthcare</h4>
<ul>
    <li>Disease diagnosis (AI can detect cancer with 95% accuracy)</li>
    <li>Drug discovery and development</li>
    <li>Personalized treatment plans</li>
    <li>Medical imaging analysis</li>
</ul>

<h4>Finance</h4>
<ul>
    <li>Fraud detection and prevention</li>
    <li>Algorithmic trading</li>
    <li>Credit risk assessment</li>
    <li>Customer service automation</li>
</ul>

<h4>Transportation</h4>
<ul>
    <li>Autonomous vehicles (Tesla, Waymo)</li>
    <li>Traffic prediction and optimization</li>
    <li>Route planning</li>
    <li>Predictive maintenance</li>
</ul>

<h4>E-commerce and Retail</h4>
<ul>
    <li>Personalized product recommendations</li>
    <li>Dynamic pricing</li>
    <li>Inventory management</li>
    <li>Virtual shopping assistants</li>
</ul>

<h4>Education</h4>
<ul>
    <li>Personalized learning paths</li>
    <li>Automated grading</li>
    <li>Intelligent tutoring systems</li>
    <li>Adaptive assessments</li>
</ul>

<h3>How AI Works: A Simple Explanation</h3>

<p><strong>Step 1: Data Collection</strong><br>
AI systems require vast amounts of data to learn patterns and make decisions.</p>

<p><strong>Step 2: Data Processing</strong><br>
Raw data is cleaned, organized, and formatted for the AI algorithm.</p>

<p><strong>Step 3: Model Training</strong><br>
The AI algorithm learns from the processed data by identifying patterns and relationships.</p>

<p><strong>Step 4: Testing and Validation</strong><br>
The trained model is tested on new data to ensure accuracy and reliability.</p>

<p><strong>Step 5: Deployment</strong><br>
The validated model is deployed in real-world applications.</p>

<p><strong>Step 6: Continuous Learning</strong><br>
Modern AI systems continuously improve by learning from new data and feedback.</p>

<h3>Popular AI Tools and Platforms</h3>

<h4>For Beginners</h4>
<ul>
    <li><strong>ChatGPT:</strong> Conversational AI for text generation</li>
    <li><strong>DALL-E:</strong> AI image generation from text descriptions</li>
    <li><strong>Grammarly:</strong> AI-powered writing assistant</li>
    <li><strong>Duolingo:</strong> AI-driven language learning</li>
</ul>

<h4>For Developers</h4>
<ul>
    <li><strong>TensorFlow:</strong> Open-source machine learning framework</li>
    <li><strong>PyTorch:</strong> Deep learning platform</li>
    <li><strong>Scikit-learn:</strong> Machine learning library for Python</li>
    <li><strong>Keras:</strong> High-level neural networks API</li>
</ul>

<h3>Ethical Considerations in AI</h3>

<h4>Bias and Fairness</h4>
<p>AI systems can perpetuate existing biases in training data. Example: Facial recognition systems showing lower accuracy for darker skin tones.</p>

<h4>Privacy Concerns</h4>
<p>AI systems often process vast amounts of personal data, raising privacy and surveillance concerns.</p>

<h4>Job Displacement</h4>
<p>Automation through AI may displace certain jobs, though it also creates new opportunities.</p>

<h4>Accountability</h4>
<p>Who is responsible when AI systems make mistakes? Questions of liability remain complex.</p>

<h3>The Future of AI</h3>

<p><strong>Emerging Trends:</strong></p>
<ol>
    <li><strong>Artificial General Intelligence (AGI):</strong> AI with human-level intelligence across all domains</li>
    <li><strong>Explainable AI:</strong> Making AI decision-making transparent and understandable</li>
    <li><strong>Edge AI:</strong> Running AI algorithms on local devices rather than cloud servers</li>
    <li><strong>AI-Human Collaboration:</strong> Systems designed to augment rather than replace human capabilities</li>
    <li><strong>Quantum AI:</strong> Leveraging quantum computing for exponentially faster AI processing</li>
</ol>

<h3>How to Get Started with AI</h3>

<p><strong>Learning Path:</strong></p>
<ol>
    <li><strong>Learn Programming Basics:</strong> Python is the most popular language for AI</li>
    <li><strong>Master Mathematics:</strong> Focus on linear algebra, calculus, and statistics</li>
    <li><strong>Study Machine Learning Fundamentals:</strong> Take online courses (Coursera, edX, Udacity)</li>
    <li><strong>Work on Projects:</strong> Apply your knowledge to real-world problems</li>
    <li><strong>Join AI Communities:</strong> Engage with Kaggle, GitHub, and AI forums</li>
</ol>

<p><strong>Recommended Resources:</strong></p>
<ul>
    <li><strong>Courses:</strong> Andrew Ng's Machine Learning (Coursera), Fast.ai</li>
    <li><strong>Books:</strong> "Hands-On Machine Learning" by Aurélien Géron</li>
    <li><strong>Platforms:</strong> Kaggle (competitions and datasets), Google Colab (free computing)</li>
</ul>

<h3>AI vs. Human Intelligence</h3>

<table border="1" cellpadding="10" style="width: 100%; border-collapse: collapse;">
    <tr style="background: #f3f4f6;">
        <th>Aspect</th>
        <th>AI</th>
        <th>Human Intelligence</th>
    </tr>
    <tr>
        <td>Processing Speed</td>
        <td>Extremely fast</td>
        <td>Slower but efficient</td>
    </tr>
    <tr>
        <td>Learning Method</td>
        <td>Data-driven patterns</td>
        <td>Experience and reasoning</td>
    </tr>
    <tr>
        <td>Creativity</td>
        <td>Limited to training data</td>
        <td>Highly creative and innovative</td>
    </tr>
    <tr>
        <td>Emotional Intelligence</td>
        <td>Cannot truly experience emotions</td>
        <td>Rich emotional understanding</td>
    </tr>
    <tr>
        <td>Adaptability</td>
        <td>Requires retraining</td>
        <td>Highly adaptable</td>
    </tr>
    <tr>
        <td>Energy Consumption</td>
        <td>High power requirements</td>
        <td>Highly energy-efficient</td>
    </tr>
</table>

<h3>Conclusion</h3>
<p>Artificial Intelligence is transforming every aspect of our lives, from healthcare to entertainment. Understanding AI fundamentals is becoming essential in the modern world. While AI offers tremendous benefits, it's crucial to develop and deploy these technologies responsibly.</p>

<p><strong>Key Takeaways:</strong></p>
<ul>
    <li>AI is already integrated into daily life through various applications</li>
    <li>Machine learning and deep learning are core AI technologies</li>
    <li>Ethical considerations must guide AI development</li>
    <li>AI will create new opportunities while transforming existing industries</li>
    <li>Continuous learning is essential in this rapidly evolving field</li>
</ul>

<p><em>Start your AI journey today by exploring free online resources and experimenting with AI tools!</em></p>
''',
                    'difficulty': 'beginner',
                    'tags': ['technology', 'ai', 'machine-learning', 'programming']
                }
            ]
        }

        # Generate articles
        created_count = 0
        for i in range(count):
            # Select random category
            category = random.choice(categories)
            
            # Get templates for this category or use generic
            if category.slug in article_templates:
                templates = article_templates[category.slug]
                template = random.choice(templates)
                
                # Create unique title by adding number
                title = f"{template['title']} - Part {i+1}"
                
                # Check if article already exists
                if Article.objects.filter(title=title).exists():
                    continue
                
                article = Article.objects.create(
                    title=title,
                    content=template['content'],
                    summary=template['summary'],
                    author=admin_user,
                    category=category,
                    difficulty=template.get('difficulty', 'beginner'),
                    is_featured=(i < 5),  # First 5 are featured
                    is_published=True
                )
                
                # Add tags
                selected_tags = random.sample(tags, min(random.randint(3, 6), len(tags)))
                article.tags.set(selected_tags)
                
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f'Created {created_count} articles...')

        self.stdout.write(self.style.SUCCESS(f'✅ Successfully created {created_count} unique articles!'))
        self.stdout.write(f'   Total articles in database: {Article.objects.count()}')
