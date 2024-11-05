import whisper
model = whisper.load_model("small")
def file2txt(path:str):
    result = model.transcribe(audio=path,verbose=True, language='ja')
    return result["text"]
print(f"Ready: {__name__}")