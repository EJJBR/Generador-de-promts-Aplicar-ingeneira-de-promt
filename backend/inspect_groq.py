from groq import Groq
import inspect, os, json
from dotenv import load_dotenv

load_dotenv()

c = Groq(api_key=os.environ.get('GROQ_API_KEY'))
sig = str(inspect.signature(c.chat.completions.create))
doc = (c.chat.completions.create.__doc__ or "")[:1500]

out = {
  "signature": sig,
  "doc_excerpt": doc
}
print(json.dumps(out, indent=2, ensure_ascii=False))
