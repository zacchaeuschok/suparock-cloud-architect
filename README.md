### AWS Suapbase Hackathon

This application demonstrates how to use Supabase for vector search and AWS services to perform image search tasks. The system leverages AWS’s powerful Bedrock model for generating embeddings and Supabase to store and retrieve these embeddings efficiently.

Features

- Image Embedding: Converts images into vector embeddings using AWS’s Bedrock model.
- Vector Storage: Utilizes Supabase’s vector capabilities to store and query image embeddings.
- Search Functionality: Allows users to search for images based on vector similarity.

Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10 or higher
- Poetry for dependency management
- Accesss to AWS services
- Access to a Supabase project

### Installation

**1. Clone the repository**

```
git clone https://github.com/yourusername/your-repository.git
cd your-repository
```

**2. Install dependencies**

```
poetry install
```

**3. Set up database:**
```
supabase start
poetry run seed_image
poetry run seed_text
```

**3. Set up environment variables:**

Create a .env file in the root directory and populate it with your AWS and Supabase credentials:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

**4. Test the application:**
```
poetry run search_image "Person lying down on grass"
poetry run search_text "Should I use a single or multiple AWS accounts?"
```
