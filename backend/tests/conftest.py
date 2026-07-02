import importlib.machinery
import sys
import types
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _create_fake_tf():
    tf = types.ModuleType('tensorflow')
    tf.__version__ = '2.15.0'
    tf.__spec__ = importlib.machinery.ModuleSpec('tensorflow', loader=None)

    keras = types.ModuleType('tensorflow.keras')
    layers = types.ModuleType('tensorflow.keras.layers')
    optimizers = types.ModuleType('tensorflow.keras.optimizers')
    metrics = types.ModuleType('tensorflow.keras.metrics')

    class FakeLayer:
        def __init__(self, *args, **kwargs):
            pass

    class FakeLayerWrapper(FakeLayer):
        pass

    class FakeModel:
        def __init__(self, layers=None):
            self.layers = layers or []

        def compile(self, *args, **kwargs):
            return None

        def predict(self, X, verbose=0):
            import numpy as np
            return np.array([[0.5]])

    class Sequential:
        def __init__(self, layers=None):
            self.layers = layers or []

        def compile(self, *args, **kwargs):
            return None

        def predict(self, X, verbose=0):
            import numpy as np
            # Return a shape that is compatible with binary classification output
            return np.full((len(X), 1), 0.5, dtype=np.float32)

    class Optimizer:
        def __init__(self, *args, **kwargs):
            pass

    class AUC:
        def __init__(self, name=None):
            self.name = name

    layers.LSTM = FakeLayerWrapper
    layers.Dropout = FakeLayerWrapper
    layers.Dense = FakeLayerWrapper

    optimizers.Adam = Optimizer
    metrics.AUC = AUC

    keras.Sequential = Sequential
    keras.Model = Sequential
    keras.layers = layers
    keras.optimizers = optimizers
    keras.metrics = metrics

    tf.keras = keras
    sys.modules['tensorflow'] = tf
    sys.modules['tensorflow.keras'] = keras
    sys.modules['tensorflow.keras.layers'] = layers
    sys.modules['tensorflow.keras.optimizers'] = optimizers
    sys.modules['tensorflow.keras.metrics'] = metrics

    # Stub SHAP and LIME to avoid import-time failures in environments without these packages
    shap = types.ModuleType('shap')
    shap.explainers = types.ModuleType('shap.explainers')
    shap.KernelExplainer = lambda *args, **kwargs: types.SimpleNamespace(
        shap_values=lambda x: [ [0.0] * len(x[0]) ],
        expected_value=[0.0, 0.0]
    )
    sys.modules['shap'] = shap
    sys.modules['shap.explainers'] = shap.explainers

    lime = types.ModuleType('lime')
    lime.lime_tabular = types.ModuleType('lime.lime_tabular')
    sys.modules['lime'] = lime
    sys.modules['lime.lime_tabular'] = lime.lime_tabular

    # Stub langchain text splitters to avoid transformers/torch import during test collection
    langchain_text_splitters = types.ModuleType('langchain_text_splitters')
    class RecursiveCharacterTextSplitter:
        def __init__(self, *args, **kwargs):
            pass

        def split_text(self, text):
            return [text]

    langchain_text_splitters.RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter
    sys.modules['langchain_text_splitters'] = langchain_text_splitters

    langchain_text_splitters_base = types.ModuleType('langchain_text_splitters.base')
    langchain_text_splitters_base.RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter
    sys.modules['langchain_text_splitters.base'] = langchain_text_splitters_base

    # Stub RAG module to avoid heavy HuggingFace/sentence-transformers initialization during backend test collection
    rag_pkg = types.ModuleType('RAG')
    rag_pkg.__path__ = []
    rag_logic = types.ModuleType('RAG.rag_logic')
    class DummyRAGManager:
        def __init__(self, *args, **kwargs):
            pass
    rag_logic.rag_manager = DummyRAGManager()
    rag_pkg.rag_logic = rag_logic
    sys.modules['RAG'] = rag_pkg
    sys.modules['RAG.rag_logic'] = rag_logic


def pytest_configure(config):
    try:
        import tensorflow as tf
        if not hasattr(tf, 'keras'):
            raise ImportError('TensorFlow installed without keras support')
    except Exception:
        _create_fake_tf()
