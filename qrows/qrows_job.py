from qiskit.providers.job import JobV1 as BaseJob
from qiskit.result import Result
from qiskit.providers.jobstatus import JobStatus
import time
import opt_einsum as oe
import torch

class QrowsJob(BaseJob):
    def __init__(self, backend, job_id, circuit):
        super().__init__(backend, job_id)
        self._circuit = circuit
        self._result = None
        self._status = JobStatus.INITIALIZING

    def submit(self):
        self._status = JobStatus.RUNNING

        # 量子ビット数を取得
        num_qubits = self._circuit.num_qubits

        # initial state vec
        psi = torch.tensor([1, 0], dtype=torch.complex128)
    
        # テンソルの情報を格納するリスト
        arr_tensor = []
        arr_state = []
        arr_arm = []
        
        # シンボルの番号
        num_symbols = 0
        
        # 量子ビットの準備
        for i in range(num_qubits):
          arr_arm.append(oe.get_symbol(num_symbols))
          arr_state.append(oe.get_symbol(num_symbols))
          arr_tensor.append(psi)
          num_symbols += 1        

        # ゲート情報を取得
        operations = self._circuit.data

        # ゲート情報に基づいてシミュレーションを行う
        for operation in operations:
            
            gate = operation[0]  # ゲート
            qubits = operation[1]  # 適用される量子ビットのリスト

            # ここで各ゲートのシミュレーションロジックを記述
            if gate.name == "x":

                # 適用される単一の量子ビットの番号
                qubit_index = qubits[0]._index
                
                # Xゲートの処理
                X = torch.tensor([[0, 1], [1, 0]], dtype=torch.complex128)

                # 1.Xゲートのアーム
                arr_arm.append(arr_state[qubit_index] + oe.get_symbol(num_symbols))

                # 2.Xゲートのテンソル
                arr_tensor.append(X)

                # 3.Xゲートの出力のアームの名前
                arr_state[qubit_index] = oe.get_symbol(num_symbols)

                # 4.シンボルの通し番号
                num_symbols += 1
                
                #print(f"Applying X gate on qubit(s) {qubit_index}")
                #print(arr_arm)
                #print(arr_tensor)
                #print(arr_state)
                #print()

            elif gate.name == "y":
            
                # 適用される単一の量子ビットの番号
                qubit_index = qubits[0]._index
            
                # Yゲートの処理
                Y = torch.tensor([[0, -1j], [1j, 0]], dtype=torch.complex128)
            
                # 1.Yゲートのアーム
                arr_arm.append(arr_state[qubit_index] + oe.get_symbol(num_symbols))
            
                # 2.Yゲートのテンソル
                arr_tensor.append(Y)
            
                # 3.Yゲートの出力のアームの名前
                arr_state[qubit_index] = oe.get_symbol(num_symbols)
            
                # 4.シンボルの通し番号
                num_symbols += 1
            
                #print(f"Applying Y gate on qubit(s) {qubit_index}")
                #print(arr_arm)
                #print(arr_tensor)
                #print(arr_state)
                #print()
            
            elif gate.name == "z":
            
                # 適用される単一の量子ビットの番号
                qubit_index = qubits[0]._index
            
                # Zゲートの処理
                Z = torch.tensor([[1, 0], [0, -1]], dtype=torch.complex128)
            
                # 1.Zゲートのアーム
                arr_arm.append(arr_state[qubit_index] + oe.get_symbol(num_symbols))
            
                # 2.Zゲートのテンソル
                arr_tensor.append(Z)
            
                # 3.Zゲートの出力のアームの名前
                arr_state[qubit_index] = oe.get_symbol(num_symbols)
            
                # 4.シンボルの通し番号
                num_symbols += 1
            
                #print(f"Applying Z gate on qubit(s) {qubit_index}")
                #print(arr_arm)
                #print(arr_tensor)
                #print(arr_state)
                #print()
            
            elif gate.name == "h":
            
                # 適用される単一の量子ビットの番号
                qubit_index = qubits[0]._index
            
                # Hゲートの処理
                H = torch.tensor([[1, 1], [1, -1]], dtype=torch.complex128) / torch.sqrt(torch.tensor(2.0, dtype=torch.complex128))
            
                # 1.Hゲートのアーム
                arr_arm.append(arr_state[qubit_index] + oe.get_symbol(num_symbols))
            
                # 2.Hゲートのテンソル
                arr_tensor.append(H)
            
                # 3.Hゲートの出力のアームの名前
                arr_state[qubit_index] = oe.get_symbol(num_symbols)
            
                # 4.シンボルの通し番号
                num_symbols += 1
            
                #print(f"Applying H gate on qubit(s) {qubit_index}")
                #print(arr_arm)
                #print(arr_tensor)
                #print(arr_state)
                #print()

            elif gate.name == "cx":

                # 適用される単一の量子ビットの番号
                control_index = qubits[0]._index
                target_index = qubits[1]._index
                
                # CNOTゲートの処理
                CX = torch.tensor([
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 0, 1],
                    [0, 0, 1, 0]
                ], dtype=torch.complex128).reshape(2,2,2,2)

                # 1.CXゲートのアーム
                arr_arm.append(arr_state[control_index] + arr_state[target_index] + oe.get_symbol(num_symbols) + oe.get_symbol(num_symbols+1))

                # 2.CXゲートのテンソル
                arr_tensor.append(CX)

                # 3.CXゲートの出力のアームの名前
                arr_state[control_index] = oe.get_symbol(num_symbols)
                arr_state[target_index] = oe.get_symbol(num_symbols+1)

                # 4.シンボルの通し番号
                num_symbols += 2
                
                #print(f"Applying CX gate on qubit(s) {control_index} and {target_index}")
                #print(arr_arm)
                #print(arr_tensor)
                #print(arr_state)

        # 結果
        equation = ','.join(arr_arm)
        
        # テンソルのリストをnumpy配列に変換
        numpy_tensors = [tensor.numpy() for tensor in arr_tensor]
        path_info = oe.contract_path(equation, *numpy_tensors)

        # 最適な計算順序（パス）を表示
        print("Optimal contraction path:")
        print(path_info)
        print()

        # 計算
        result = torch.einsum(equation, *arr_tensor).reshape(2**num_qubits)

        # テンソルをnumpy配列に変換
        result_numpy = result.numpy()

        #print(result)

        # Qiskit Resultオブジェクトに結果を設定
        self._result = Result(
            backend_name=self.backend().name(),
            backend_version='1.0',
            qobj_id=self.job_id(),  # ここでjob_idを使用
            job_id=self.job_id(),
            success=True,
            results=[{
                #'shots': 1024,
                'data': {'state_vec': result_numpy},
                'header': {'name': self._circuit.name},  # 回路名を使用
                'status': 'DONE'
            }]
        )
        self._status = JobStatus.DONE

    def result(self) -> Result:
        # 結果の取得
        return self._result

    def status(self):
        # ジョブの現在のステータスを返す
        return self._status
