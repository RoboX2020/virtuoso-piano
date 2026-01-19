import mediapipe as mp
try:
    print("Direct attributes:", dir(mp))
    print("Solutions?", hasattr(mp, 'solutions'))
    import mediapipe.python.solutions.hands
    print("Imported mediapipe.python.solutions.hands")
    print("Solutions after import?", hasattr(mp, 'solutions'))
except Exception as e:
    print(e)
