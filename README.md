# arxiv-document-ocr
Pipeline specifically curated for processing arxiv dataset for pre-training the foundational model for document understanding

### Step 1 : Install Requirements
You may create and use a virtual environment to install the following dependencies
```
pip install -r requirements.in
```

### Step 2 : Run the pipeline
Use main.py to set the parameters of input file, output set name, language.
```
python3 main.py
```

### Step 3 : Using the UI
You can also use the streamlit UI to execute the pipeline and download the compressed output. 
```
streamlit run app.py
```

### Step 3 : Visualize the results
You can also use the streamlit UI to upload the compressed output and see the rendered results
```
streamlit run visualize.py
```
