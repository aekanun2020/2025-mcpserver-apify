# วันที่ 2: Social Listening & Sentiment Analysis ด้วย Apify + n8n
## (เจาะลึกการสร้าง Agent นักสืบ Social Media)

---

## ช่วงเช้า (09:00 - 12:00): เข้าใจ Social Listening และพลังของ Apify

### อธิบายแนวคิด Social Listening และความสำคัญในยุคดิจิทัล: ทำไมองค์กรต้องฟังเสียงลูกค้าบนโลกออนไลน์?

Social Listening หรือการฟังเสียงสังคมออนไลน์เป็นกระบวนการติดตามและวิเคราะห์การสนทนาเกี่ยวกับแบรนด์ ผลิตภัณฑ์ หรือหัวข้อที่เกี่ยวข้องกับองค์กรบนแพลตฟอร์มโซเชียลมีเดียต่างๆ นี่ไม่ใช่แค่การตรวจสอบคอมเมนต์หรือการกล่าวถึงแบรนด์เท่านั้น แต่เป็นการเข้าใจลึกถึงความรู้สึก ความคิดเห็น และพฤติกรรมของผู้บริโภคในเชิงลึก

ในยุคดิจิทัลปัจจุบัน ผู้คนใช้เวลาบนโซเชียลมีเดียโดยเฉลี่ยมากกว่า 2.5 ชั่วโมงต่อวัน และใช้แพลตฟอร์มต่างๆ เป็นช่องทางหลักในการแสดงความคิดเห็น รีวิวผลิตภัณฑ์ และแบ่งปันประสบการณ์ การที่องค์กรสามารถเข้าถึงและเข้าใจข้อมูลเหล่านี้ได้จึงกลายเป็นความได้เปรียบทางการแข่งขันที่สำคัญ

การทำ Social Listening อย่างมีประสิทธิภาพช่วยให้องค์กรสามารถตอบสนองต่อปัญหาได้รวดเร็ว ปรับปรุงผลิตภัณฑ์และบริการตามความต้องการจริงของลูกค้า และสร้างกลยุทธ์การตลาดที่ตรงจุดมากขึ้น นอกจากนี้ยังช่วยในการวิเคราะห์คู่แข่ง ติดตามเทรนด์ใหม่ๆ และระบุโอกาสทางธุรกิจที่อาจเกิดขึ้น

องค์กรที่ทำ Social Listening ได้ดีมักจะมีความสัมพันธ์กับลูกค้าที่แข็งแกร่งกว่า เพราะลูกค้ารู้สึกว่าเสียงของตนเองได้รับการรับฟังและตอบสนอง การสร้างความไว้วางใจและความภักดีของลูกค้าในยุคปัจจุบันจึงไม่ใช่เรื่องของการโฆษณาเพียงอย่างเดียว แต่เป็นเรื่องของการมีปฏิสัมพันธ์ที่แท้จริงและการแสดงให้เห็นว่าองค์กรให้ความสำคัญกับความคิดเห็นของลูกค้า

**อ้างอิง:**
- Sprout Social Research: https://sproutsocial.com/insights/social-listening/
- Hootsuite Social Media Trends Report: https://hootsuite.com/resources/social-trends
- Sprinklr: Social Listening Guide 2025: https://www.sprinklr.com/blog/social-listening/
- Brandwatch Social Listening Tools: https://www.brandwatch.com/blog/social-listening-tools/
- Emplifi: Social Listening Tools Overview: https://emplifi.io/resources/blog/social-listening-tools/
- Determ: Best Social Media Sentiment Analysis Tools 2025: https://determ.com/blog/best-social-media-sentiment-analysis-tools/

---

### แนะนำ Apify และ Actors สำหรับ Social Media: เครื่องมือทรงพลังในการดึงข้อมูลจาก Facebook, Instagram, TikTok และแพลตฟอร์มอื่นๆ

Apify เป็นแพลตฟอร์มระบบคลาวด์ที่ออกแบบมาเพื่อการทำ Web Scraping และ Data Extraction อย่างมืออาชีพ โดยเฉพาะสำหรับการเก็บข้อมูลจากเว็บไซต์และแพลตฟอร์มโซเชียลมีเดียต่างๆ ที่มีความซับซ้อนสูง สิ่งที่ทำให้ Apify โดดเด่นคือระบบ "Actors" ซึ่งเป็นโปรแกรมเล็กๆ ที่ถูกสร้างขึ้นมาเฉพาะเจาะจงสำหรับการดึงข้อมูลจากแหล่งข้อมูลต่างๆ

Actors ใน Apify ทำงานเหมือนกับหุ่นยนต์ดิจิทัลที่สามารถเลียนแบบพฤติกรรมของมนุษย์ในการท่องเว็บ การคลิก การเลื่อนหน้า และการกรอกข้อมูลได้ สำหรับโซเชียลมีเดีย Actors เหล่านี้สามารถจัดการกับความซับซ้อนของระบบป้องกันและการโหลดเนื้อหาแบบไดนามิกที่แพลตฟอร์มต่างๆ ใช้ได้อย่างมีประสิทธิภาพ

**อ้างอิง:**
- Apify Store: https://apify.com/store
- Apify Documentation: https://docs.apify.com/
- Apify Platform Overview: https://apify.com
- How to Scrape a Website (Apify Blog): https://blog.apify.com/how-to-scrape-website/
- Instagram Scraper Comparison: https://research.aimultiple.com/instagram-scraping/
- YouTube: Apify FULL GUIDE 2025: https://www.youtube.com/watch?v=KQIo1gNFAeM
- Social Media Email Scraper API: https://apify.com/chitosibug3/social-media-email-scraper-2025/api/openapi
- Firecrawl vs Apify 2025 Comparison: https://blackbearmedia.io/firecrawl-vs-apify/

---

## Workshop: เริ่มต้นใช้งาน Apify ดึงโพสต์/คอมเมนต์ และวิเคราะห์ Sentiment อัตโนมัติ

**อ้างอิง:**
- Apify Academy: https://docs.apify.com/academy
- Hugging Face Sentiment Analysis: https://huggingface.co/docs/transformers/tasks/sentiment_analysis
- iApp Thai Sentimental Analysis: https://iapp.co.th/docs/nlp-ai/thai-sentimental
- Repustate Thai Sentiment Analysis: https://www.repustate.com/thai-sentiment-analysis/
- AI Sentiment Tools Comparison: https://superagi.com/ai-sentiment-analysis-tools-comparison-sprout-social-brandwatch-and-sentisum-which-one-is-right-for-you/
- Sprout API Docs: https://api.sproutsocial.com/docs/
- Brandwatch Listen Module: https://social-media-management-help.brandwatch.com/hc/en-us/articles/4497719399453-Introduction-to-Listen

---

## ช่วงบ่าย (13:00 - 16:30): สร้างระบบ Social Listening อัตโนมัติด้วย Apify + n8n

### Workshop: เชื่อมต่อ Apify กับ n8n เพื่อสรุปข้อมูล/แจ้งเตือน/สร้างรายงานอัตโนมัติ

**อ้างอิง:**
- n8n Documentation: https://docs.n8n.io/
- n8n Homepage: https://n8n.io/
- Getting Started with n8n: https://www.movestax.com/post/getting-started-with-n8n-workflow-automation-basics
- GitHub: n8n Workflows Collection: https://github.com/Zie619/n8n-workflows
- Auto Document n8n Workflows: https://n8n.io/workflows/2173-auto-document-your-n8n-workflows/
- Crisis Monitoring with n8n: https://www.upskillist.com/blog/how-to-monitor-social-media-for-crisis-signals/

---

### Workshop: สร้าง Dashboard หรือรายงานสรุป Mention และ Sentiment

**อ้างอิง:**
- Tableau Learning: https://www.tableau.com/learn
- Google Data Studio Help: https://support.google.com/datastudio/
- Sprout API: https://api.sproutsocial.com/docs/
- Hootsuite API (Pipedream): https://pipedream.com/apps/hootsuite
- Social Media Monitoring Tools (Blogging Wizard): https://bloggingwizard.com/social-media-monitoring-tools/
- Social Sentiment Guide (GetThematic): https://getthematic.com/insights/social-media-sentiment-analysis/

---

### แชร์ตัวอย่างการใช้งานจริง (Real-world Use Cases) และ Q&A

**อ้างอิง:**
- Social Media Examiner: https://www.socialmediaexaminer.com/
- Buffer Blog: https://buffer.com/library/
- Brandwatch Guide: https://www.brandwatch.com/blog/social-listening-guide/
- Quorage Strategy Guide: https://quorage.com/social-media/social-listening-guide-strategy/
- Crisis Management Tools (Sprout): https://sproutsocial.com/insights/crisis-management-tools/

---

## Best Practices & Tool Comparisons

**อ้างอิง:**
- Social Intelligence Platforms 2025: https://www.britopian.com/social/social-intelligence-platforms-2025/
- Affinity: Hot Social Listening 2025: https://affinity.co.th/hot-social-listening-2025/
- Martech Mafia Review: https://martechmafia.net/technology/review-social-listening-tools-thailand/
- Emplifi: https://emplifi.io/resources/blog/social-listening-tools/
- Determ: https://determ.com/blog/best-social-media-sentiment-analysis-tools/

---

*สามารถนำเอกสารนี้ไปใช้ร่วมกับไฟล์ .md เดิม โดยเพิ่มส่วนอ้างอิงที่ท้ายแต่ละหัวข้อ*