from langgraph.store.memory import InMemoryStore
import uuid

store = InMemoryStore()
user_id = "1"
namespace = (user_id, "memories")

memory_id = str(uuid.uuid4())
memory = {"food_preference": "I like pizza"}
store.put(namespace, memory_id, memory)

# récupérer les souvenirs
memories = store.search(namespace)
print(memories[-1].dict())
