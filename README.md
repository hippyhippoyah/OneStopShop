# OneStopShop: WIP

OneStopShop is a comprehensive platform that simplifies product research by gathering information from multiple sources. With OneStopShop, the website automatically:

- **Access YouTube Reviews**: See video reviews for your products.
- **Read Online Reviews**: Aggregate reviews from various online sources.
- **Ask AI**: Get insights and answers from our AI-powered assistant.

And Based on this information, it gives you the top 5 Products!

## Architecture

The system is composed of the following components:

1. **Frontend**: Built with Next.js
   - Handles user interface and interactions.
   - Communicates with the backend through the `page.js` and `next.config.mjs` files.

2. **Backend**: Implemented using Flask (Python)
   - Manages API requests and data processing.
   - Interacts with the Chroma vector database through a network bridge. Refer to `docker-compose.yml` and `parser.py` for details.

3. **ChromaDB**: Vector database used for Retrieval-Augmented Generation (RAG) computing.

## Setup and Running the Application

Follow these steps to set up and run OneStopShop:

1. **Create Environment Variables**:
   - In the `/server` directory, create a `.env` file.
   - Add the following variables with your respective API keys:
     ```env
     OPENAI_API_KEY=<your_openai_api_key>
     SERPER_API_KEY=<your_serper_api_key>
     ```
   - You can obtain these API keys by searching for instructions online on how to get them.

2. **Build and Run with Docker**:
   - Ensure Docker is installed and running on your machine.
   - Open a terminal and navigate to the root directory of the project.
   - Execute the following command to build and start all containers:
     ```bash
     docker-compose up --build
     ```

## Important Files

- `page.js` and `next.config.mjs`: Configuration and communication setup for the frontend.
- `docker-compose.yml`: Defines the Docker setup and network bridge.
- `parser.py`: Handles the interaction between the backend and the ChromaDB.


## Contact

For any questions or support, please reach out to f2bcoding.business@gmail.com

---

Happy researching with OneStopShop!
