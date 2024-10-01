<img src="images/box-pinecone.png" 
alt= “box-pinecone” 
style="margin-left:-10px;"
width=100%;>

# Box and Pinecone Integration Sample

This project demonstrates how to integrate Box and Pinecone via a python script. This coincides with a blog post on Medium. Please see that posting for more insructuctions on how to use this solution.

LINK TO BLOG

You will need accounts for Box, Pinecone, and OpenAI to appropriate run this demo. You will also need an OAuth Box custom application created in the Box Developer Console.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/box-pinecone-sample.git
   ```
   ```bash
   cd box-pinecone-sample

2. Create and activate a virtual environment:
    ```bash 
    python3 -m venv venv
    source venv/bin/activate
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
4. Create config.py file.  
   ```bash
   cp sample_config.py config.py
5. Open the code in an editor of your choice. Update the credentials/Box folder ID with the information you create based on the above linked Medium Post. Save the file.
> [!IMPORTANT]  
> DO NOT input 0 as the folder id. This will attempt to index your entire Box account. Not only is this not recommended, it will exceed rate limits, cost lots of money, and probably break.
6. To create embeddings:
   ```bash
   python main.py
7. To answer queries about the created embeddings: 
   ```bash
   python query.py
