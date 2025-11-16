# Robust TorchServe handler for Asteria anomaly model (state_dict-based)
import os
import sys
import json
import torch
import traceback
from ts.torch_handler.base_handler import BaseHandler

def log(*args, **kwargs):
    print("[ASTERIA_HANDLER]", *args, **kwargs, flush=True)

def ensure_paths(model_dir):
    if model_dir not in sys.path:
        sys.path.insert(0, model_dir)
    ml_path = os.path.join(model_dir)
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)
    log("sys.path first entries:", sys.path[:4])

class AsteriaHandler(BaseHandler):
    def initialize(self, context):
        try:
            self.context = context
            model_dir = context.system_properties.get("model_dir") or "."
            ensure_paths(model_dir)
            log("Model dir:", model_dir)

            ModelClass = None
            tried = []
            for modname in ("ml.models.anomaly_model", "anomaly_model", "models.anomaly_model"):
                try:
                    mod = __import__(modname, fromlist=["AnomalyLSTM"])
                    ModelClass = getattr(mod, "AnomalyLSTM")
                    log(f"Imported AnomalyLSTM from {modname}")
                    break
                except Exception as e:
                    tried.append((modname, str(e)))

            if ModelClass is None:
                log("Import attempts failed:", tried)
                raise ImportError("Could not import AnomalyLSTM from any known path")

            model_path = os.path.join(model_dir, "model.pt")
            log("Attempting to load model from:", model_path)
            state = torch.load(model_path, map_location="cpu")
            self.model = ModelClass()
            if isinstance(state, dict) and "state_dict" in state:
                self.model.load_state_dict(state["state_dict"])
            elif isinstance(state, dict) and set(state.keys()) & set(self.model.state_dict().keys()):
                self.model.load_state_dict(state)
            else:
                try:
                    self.model = state
                except Exception:
                    raise RuntimeError("Loaded object not recognized as state_dict or model")

            self.model.eval()
            log("Model loaded and eval() set.")
        except Exception:
            log("Exception in initialize():")
            traceback.print_exc()
            raise

    def preprocess(self, data):
        try:
            if not data:
                return {}
            body = data[0].get("body")
            if isinstance(body, (bytes, bytearray)):
                body = body.decode("utf-8")
            if isinstance(body, str):
                payload = json.loads(body)
            elif isinstance(body, dict):
                payload = body
            else:
                raise ValueError("Unsupported body type")
            return payload
        except Exception:
            log("Exception in preprocess():")
            traceback.print_exc()
            raise

    def inference(self, payload):
        try:
            emb = payload.get("embedding", [])
            feats = payload.get("features", [])

            emb_t = torch.tensor(emb).float()
            feats_t = torch.tensor(feats).float()

            if emb_t.ndim == 1:
                emb_t = emb_t.unsqueeze(0).unsqueeze(0)
            elif emb_t.ndim == 2:
                emb_t = emb_t.unsqueeze(0)

            if feats_t.ndim == 1:
                feats_t = feats_t.unsqueeze(0).unsqueeze(0)
            elif feats_t.ndim == 2:
                feats_t = feats_t.unsqueeze(0)

            try:
                x = torch.cat([emb_t, feats_t], dim=-1)
            except Exception:
                x = torch.cat([emb_t.view(1, -1), feats_t.view(1, -1)], dim=-1).unsqueeze(1)

            with torch.no_grad():
                out = self.model(x)
                if isinstance(out, torch.Tensor):
                    score = out.squeeze().item()
                else:
                    score = float(out)

            return {"anomaly_score": score}
        except Exception:
            log("Exception in inference():")
            traceback.print_exc()
            raise

    def postprocess(self, inference_output):
        try:
            return [json.dumps(inference_output)]
        except Exception:
            log("Exception in postprocess():")
            traceback.print_exc()
            raise

    