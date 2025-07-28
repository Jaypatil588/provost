from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
vector_store_details = {
    "id": os.getenv("VECTORDBID"),
}
vector_store_id = os.getenv("VECTORDBID")
app = Flask(__name__)
# api = os.getenv("OPENAI")

client = OpenAI()

#toggle guard rails here if any complications in the generations.
#The main idea is that we use a request to determine relevancy first, then pass on to generation.
enableGuardrails = True

def checkInput(input):
    objective = "Santa Clara University (SCU), Provost, Education advising, courses, academic policies, or student advising and support"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": f"You will receive a user query and your task is to classify if a given user request is related to {objective}. If it is relevant, return `1`. Else, return `0`"},
        {"role": "user", "content": input},
        ],
        seed=0,
        temperature=0,
        max_tokens=1,
        logit_bias={"15": 100, #token ID for `0` 
                    "16": 100})  #token ID for `1`
    #print(response)
    return int(response.choices[0].message.content)

def generateResponse(query,vector_store_id):
    
    instructions = """
    You are an expert SCU academic advisor. Your role is to provide direct, concise, accurate, and complete answers using only the provided university documents.
    Before answering, break down the user's question, search all provided documents for every piece of relevant information, and then synthesize a single, direct answer.
    Answering Rules:
    - For Course Questions with Multiple Requirements (e.g., "Arts AND Ethics"): Your primary task is to find the intersection. First, identify all courses that meet each separate requirement. Then, provide a single, final list containing only the courses that satisfy all conditions. Group this list by department with full course numbers and titles.
    - For Policy Questions (e.g., "Can I double dip?"): Identify the specific policy and summarize the relevant rules, conditions, or exceptions. If the user mentions their status (e.g., "as a transfer student"), apply the rules specifically to their situation.
    - Final Answer: Always be direct and complete. Do not suggest reading a source document; extract the information and present it clearly. If no information is found or no courses meet the criteria, state that explicitly.
    """

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=query,
            temperature=0.0,
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
                "max_num_results": 30,
            }],
            include=["file_search_call.results"],
            instructions=instructions,
        )
        
        # Extract the message text from the response
        message_text = next((item.content[0].text for item in response.output if item.type == 'message'), None) # type: ignore

        if message_text:
            return jsonify({"response": message_text})
        else:
            return jsonify({"response": "Error in generating response."}), 500

    except Exception as e:
        # Handle potential API errors
        return jsonify({"error": str(e)}), 500

# Define the main endpoint for processing user queries
@app.route('/bot', methods=['POST'])
def get_response():
    # Get the JSON data from the request body
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Request body must be JSON and contain a 'query' key."}), 400

    query = data['query']
    isValid = 0
    if enableGuardrails == True:
        isValid = checkInput(query)

    #print(isValid)
    if not vector_store_id:
        return jsonify({"error": "VECTORDBID environment variable not set."}), 500

    if (enableGuardrails == True and isValid == 1) or enableGuardrails == False:
        return generateResponse(query,vector_store_id)
    else:
        return jsonify({"response": "Sorry, i cannot help you with that!"})

# Define a health check endpoint, default
@app.route('/')
def check():
    """
    A simple endpoint to confirm that the Flask application is running.
    """
    return jsonify({"status": "ok", "message": "Provost Bot API is running."})


# Note: For local development, you might add the following lines.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


