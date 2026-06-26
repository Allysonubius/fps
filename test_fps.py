import time
import sys

# Importa as funções do seu módulo core.fps
from core.fps import start_presentmon, stop_presentmon, fps_data

def run_test():
    print("=" * 50)
    print("INICIANDO TESTE DO PRESENTMON")
    print("ATENÇÃO: O terminal DEVE estar rodando como Administrador!")
    print("=" * 50)
    
    # Inicia o monitoramento em background
    start_presentmon()
    
    print("\nAguardando dados... (Abra algum jogo ou aplicação 3D)\n")
    
    try:
        # Loop infinito para mostrar os dados capturados
        while True:
            fps = fps_data.get("fps", 0.0)
            frametime = fps_data.get("frametime", 0.0)
            processo = fps_data.get("process", "Nenhum")
            
            # Printa os dados a cada segundo
            print(f"Processo: {processo: <20} | FPS: {fps: <6} | Frametime: {frametime} ms")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Quando você apertar Ctrl+C no terminal, ele para o processo
        print("\nTeste interrompido pelo usuário.")
        stop_presentmon()
        sys.exit(0)

if __name__ == "__main__":
    run_test()