from qiskit.providers import BackendV1
from qiskit.providers.models import BackendConfiguration
from qiskit.providers.options import Options
from .qrows_job import QrowsJob

class QrowsBackend(BackendV1):
    def __init__(self):
        configuration = BackendConfiguration(
            backend_name='qrows_backend',
            backend_version='1.0',
            n_qubits=5,
            basis_gates=['u1', 'u2', 'u3', 'cx', 'id'],
            gates=[],
            local=True,
            simulator=True,
            conditional=False,
            open_pulse=False,
            memory=False,
            max_shots=1024,
            coupling_map=None,
        )
        super().__init__(configuration)

    @classmethod
    def _default_options(cls) -> Options:
        # デフォルトのオプションを定義
        return Options(shots=1024, memory=False)

    def run(self, circuit: 'QuantumCircuit') -> QrowsJob:
        job_id = str(hash(circuit.name))  # QuantumCircuitの名前をハッシュしてジョブIDを生成
        job = QrowsJob(self, job_id, circuit)  # QrowsJobのインスタンスを作成
        job.submit()  # ジョブの実行
        return job
