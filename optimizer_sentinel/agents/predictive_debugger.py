from ..adapters.anomalymodeladapter import AnomalyModel
from ..workflows.forecastandpatch import forecastandpatch
from ..storage.neo4j_anchor import anchor_forecast

class PredictiveDebugger:
    def __init__(self):
        self.model = AnomalyModel()

    def monitor_trace(self, trace: str, source: str):
        forecast = self.model.predict(trace)
        patch = forecastandpatch(forecast)
        anchor_forecast(source, forecast, patch)
        return patch
