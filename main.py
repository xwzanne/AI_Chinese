from flask import Flask, render_template, request, jsonify 
from openai import OpenAI
from password import API_KEY, PROJECT_ID, ORGANIZATION

app = Flask(__name__) 

# OpenAI API Key 

PROMPT_PREFIX = """
You are a tutor in writing Chinese characters. You know 2 functions: show_character_writing and practice_character, they both take 1 string parameter as input. Given user input please decide which function to call. When the user input is not related to these functions, respond 'None'.
For example:
Input: Do you know how to write '你好'?
Function: show_character_writing
parameter: 你好

Input: Help me practice to write 早上好
Function: practice_character
parameter: 早上好

Input: Who are you
Function: None

Input: """

def get_completion(input, prompt_prefix=''): 
    client = OpenAI(api_key=API_KEY, organization=ORGANIZATION, project=PROJECT_ID)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt_prefix + input}
        ]
    )

    response = completion.choices[0].message
    return response

def parse_response(output):
    lines = output.split("\n")
    func_name = None
    parameter = None
    for line in lines:
        ll = line.lower().strip()
        if "function:" in ll and func_name is None:
            func_name = ll[len("function: "):]
        if "parameter" in ll and parameter is None:
            parameter = ll[len("parameter: "):]
    return func_name, parameter

def take_action(input, func_name, parameter):
    if func_name == 'practice_character' or func_name=='show_character_writing':
        if len(parameter) > 5:
            return {"response": f"You are requesting too many characters, please reduce your request to maximum 5 characters."}
        else:
            return {"func_name": func_name, "param": parameter}
    else:
        return {"response": get_completion(input).content}

@app.route("/", methods=['POST', 'GET']) 
def query_view(): 
    if request.method == 'POST': 
        raw_input = request.form['input']
        print('Getting request:', raw_input)
        # if raw_input == 'scw':
        #     return jsonify({"func_name": 'show_character_writing', "param":"你好"})
        # if raw_input == 'pc':
        #     return jsonify({"func_name": 'pc', "param":"你好"})
        # else:
        #     return jsonify({"response": "debugging"})
        response = get_completion(raw_input, PROMPT_PREFIX)
        print('Got response from ChatGPT:', response)
        func_name, param = parse_response(response.content)
        print("func_name:", func_name)
        print("param:", param)
        return jsonify(take_action(raw_input, func_name, param)) 
    return render_template('index.html')


if __name__ == "__main__": 
    app.run(debug=True) 
