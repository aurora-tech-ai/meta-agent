#!/usr/bin/env python3
"""
META-AGENT: Gerador Autônomo de Agentes IA
Cria, revisa e empacota agentes Flask minimalistas com IA
Modo autônomo: gera agentes sem interação humana
"""

import os
import sys
import json
import shutil
import zipfile
import anthropic
import uuid
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class MetaAgent:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.agents_dir = Path('agents')
        self.agents_dir.mkdir(exist_ok=True)
        
        # Templates de agentes disponíveis
        self.agent_templates = {
            'conversational': {
                'label': 'Conversacional',
                'description': 'Agente para conversas naturais e assistência geral',
                'system_prompt': 'Você é um assistente conversacional amigável e útil.'
            },
            'legal': {
                'label': 'Jurídico',
                'description': 'Especialista em direito e questões legais',
                'system_prompt': 'Você é um assistente jurídico especializado em direito brasileiro.'
            },
            'medical': {
                'label': 'Médico',
                'description': 'Assistente para informações de saúde',
                'system_prompt': 'Você é um assistente médico que fornece informações educacionais sobre saúde.'
            },
            'developer': {
                'label': 'Programador',
                'description': 'Especialista em desenvolvimento de software',
                'system_prompt': 'Você é um programador experiente especializado em múltiplas linguagens.'
            },
            'data_analyst': {
                'label': 'Analista de Dados',
                'description': 'Especialista em análise e visualização de dados',
                'system_prompt': 'Você é um analista de dados especializado em insights e visualizações.'
            },
            'creative': {
                'label': 'Criativo',
                'description': 'Escritor criativo e gerador de conteúdo',
                'system_prompt': 'Você é um escritor criativo especializado em storytelling e conteúdo engajador.'
            },
            'educator': {
                'label': 'Educador',
                'description': 'Professor e facilitador de aprendizado',
                'system_prompt': 'Você é um educador paciente e didático que adapta explicações ao nível do aluno.'
            },
            'financial': {
                'label': 'Financeiro',
                'description': 'Consultor financeiro e de investimentos',
                'system_prompt': 'Você é um consultor financeiro que oferece orientação educacional sobre finanças.'
            }
        }

    def generate_custom_prompt(self, agent_type: str, agent_name: str) -> str:
        """Usa Claude para gerar um prompt customizado e específico para o agente"""
        template = self.agent_templates.get(agent_type, self.agent_templates['conversational'])
        
        prompt_generation_request = f"""Crie um system prompt detalhado e específico para um agente IA do tipo {template['label']}.

Nome do agente: {agent_name}
Tipo: {agent_type}
Descrição base: {template['description']}

O prompt deve:
1. Ser específico e detalhado para o tipo de agente
2. Incluir personalidade única e características distintivas
3. Definir claramente as capacidades e limitações
4. Estabelecer tom de voz e estilo de comunicação
5. Incluir exemplos de como responder
6. Ser em português brasileiro
7. Ter entre 150-300 palavras

Crie um prompt profissional, criativo e que torne este agente único e valioso.
Retorne APENAS o prompt, sem explicações adicionais."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.8,
                messages=[{
                    "role": "user",
                    "content": prompt_generation_request
                }]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            print(f"⚠️  Erro ao gerar prompt customizado: {e}")
            return template['system_prompt']

    def generate_agent_name(self, agent_type: str) -> str:
        """Gera um nome único para o agente com UUID"""
        template = self.agent_templates.get(agent_type, self.agent_templates['conversational'])
        base_name = template['label'].lower().replace(' ', '_')
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_name}_{unique_id}"

    def autonomous_create_agent(self, agent_type: str) -> Dict[str, any]:
        """Cria um agente de forma completamente autônoma"""
        print(f"\n🤖 Iniciando criação autônoma de agente tipo: {agent_type}")
        
        # Gera nome único
        agent_name = self.generate_agent_name(agent_type)
        print(f"📝 Nome gerado: {agent_name}")
        
        # Gera prompt customizado usando Claude
        print(f"🧠 Gerando prompt customizado com Claude 3.5 Sonnet...")
        custom_prompt = self.generate_custom_prompt(agent_type, agent_name)
        print(f"✅ Prompt customizado gerado com sucesso!")
        
        # Cria estrutura do agente
        print(f"🏗️  Criando estrutura do agente...")
        agent_path = self.generate_agent_structure(agent_name, agent_type, custom_prompt)
        
        # Revisa automaticamente
        print(f"🔍 Revisando código gerado...")
        review_results = self.review_agent(agent_path)
        
        # Cria ZIP automaticamente
        print(f"📦 Empacotando agente...")
        zip_file = self.create_agent_zip(agent_path)
        
        # Retorna informações do agente criado
        result = {
            'name': agent_name,
            'type': agent_type,
            'path': str(agent_path),
            'zip': zip_file,
            'prompt': custom_prompt[:200] + '...' if len(custom_prompt) > 200 else custom_prompt,
            'created_at': datetime.now().isoformat()
        }
        
        # Salva log de criação
        self._save_creation_log(result)
        
        print(f"\n✨ Agente criado com sucesso!")
        print(f"📁 Localização: {agent_path}")
        print(f"📦 ZIP: {zip_file}")
        
        return result

    def autonomous_batch_create(self, count: int = 5, types: Optional[List[str]] = None):
        """Cria múltiplos agentes de forma autônoma"""
        if types is None:
            types = list(self.agent_templates.keys())
        
        print(f"\n🚀 Iniciando criação autônoma de {count} agentes...")
        created_agents = []
        
        for i in range(count):
            agent_type = types[i % len(types)]
            print(f"\n[{i+1}/{count}] Criando agente...")
            
            try:
                agent_info = self.autonomous_create_agent(agent_type)
                created_agents.append(agent_info)
            except Exception as e:
                print(f"❌ Erro ao criar agente: {e}")
                continue
        
        # Gera relatório final
        self._generate_batch_report(created_agents)
        
        return created_agents

    def _save_creation_log(self, agent_info: Dict):
        """Salva log de criação dos agentes"""
        log_file = self.agents_dir / 'creation_log.json'
        
        # Carrega log existente ou cria novo
        if log_file.exists():
            with open(log_file, 'r') as f:
                log = json.load(f)
        else:
            log = {'agents': []}
        
        # Adiciona novo agente
        log['agents'].append(agent_info)
        
        # Salva log atualizado
        with open(log_file, 'w') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    def _generate_batch_report(self, agents: List[Dict]):
        """Gera relatório HTML dos agentes criados"""
        report_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Agentes Criados - {datetime.now().strftime('%d/%m/%Y %H:%M')}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white p-8">
    <div class="max-w-6xl mx-auto">
        <h1 class="text-4xl font-bold mb-8">📊 Relatório de Criação de Agentes</h1>
        <div class="bg-gray-800 rounded-lg p-6 mb-8">
            <p class="text-xl">Total de agentes criados: <span class="text-green-400 font-bold">{len(agents)}</span></p>
            <p class="text-gray-400">Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="grid gap-6">
"""
        
        for agent in agents:
            template = self.agent_templates.get(agent['type'], {})
            report_content += f"""
            <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h2 class="text-2xl font-bold text-blue-400">{agent['name']}</h2>
                        <p class="text-gray-400">Tipo: {template.get('label', agent['type'])}</p>
                    </div>
                    <span class="px-3 py-1 bg-green-600/20 text-green-400 rounded-full text-sm">
                        ✅ Criado
                    </span>
                </div>
                <div class="space-y-2 text-sm">
                    <p><strong>Prompt:</strong> {agent['prompt']}</p>
                    <p><strong>Caminho:</strong> <code class="bg-gray-900 px-2 py-1 rounded">{agent['path']}</code></p>
                    <p><strong>ZIP:</strong> <code class="bg-gray-900 px-2 py-1 rounded">{agent['zip']}</code></p>
                    <p><strong>Criado em:</strong> {agent['created_at']}</p>
                </div>
            </div>
"""
        
        report_content += """
        </div>
    </div>
</body>
</html>"""
        
        report_path = self.agents_dir / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"\n📊 Relatório gerado: {report_path}")

    def generate_agent_structure(self, agent_name: str, agent_type: str, custom_prompt: Optional[str] = None) -> Path:
        """Gera a estrutura completa de um agente"""
        agent_path = self.agents_dir / agent_name
        agent_path.mkdir(exist_ok=True)
        
        # Cria subdiretórios
        (agent_path / 'templates').mkdir(exist_ok=True)
        (agent_path / 'static').mkdir(exist_ok=True)
        (agent_path / 'static' / 'css').mkdir(exist_ok=True)
        (agent_path / 'static' / 'js').mkdir(exist_ok=True)
        
        # Gera arquivos
        self._create_app_py(agent_path, agent_name, agent_type, custom_prompt)
        self._create_index_html(agent_path, agent_name, agent_type)
        self._create_requirements_txt(agent_path)
        self._create_env_file(agent_path)
        self._create_dockerfile(agent_path, agent_name)
        self._create_readme(agent_path, agent_name, agent_type)
        self._create_landing_page(agent_path, agent_name, agent_type)  # Nova função!
        
        return agent_path

    def _create_app_py(self, path: Path, name: str, agent_type: str, custom_prompt: Optional[str]):
        """Cria o arquivo app.py principal"""
        template = self.agent_templates.get(agent_type, self.agent_templates['conversational'])
        system_prompt = custom_prompt or template['system_prompt']
        
        app_content = f'''import os
from flask import Flask, render_template, request, jsonify
import anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Configuração do agente
AGENT_CONFIG = {{
    'name': '{name}',
    'type': '{agent_type}',
    'label': '{template["label"]}',
    'description': '{template["description"]}',
    'model': 'claude-3-5-sonnet-20241022',
    'max_tokens': 4096
}}

SYSTEM_PROMPT = """{system_prompt}"""

@app.route('/')
def index():
    return render_template('index.html', config=AGENT_CONFIG)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        response = client.messages.create(
            model=AGENT_CONFIG['model'],
            max_tokens=AGENT_CONFIG['max_tokens'],
            temperature=0.7,
            system=SYSTEM_PROMPT,
            messages=[
                {{"role": "user", "content": user_message}}
            ]
        )
        
        return jsonify({{
            'response': response.content[0].text,
            'timestamp': datetime.now().isoformat()
        }})
        
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500

@app.route('/health')
def health():
    return jsonify({{'status': 'healthy', 'agent': AGENT_CONFIG}})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        
        with open(path / 'app.py', 'w') as f:
            f.write(app_content)

    def _create_index_html(self, path: Path, name: str, agent_type: str):
        """Cria o arquivo index.html com UI moderna"""
        html_content = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Agente IA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-900 text-gray-100">
    <div x-data="chatApp()" class="min-h-screen flex flex-col">
        <!-- Header -->
        <header class="bg-gray-800 shadow-lg border-b border-gray-700">
            <div class="max-w-4xl mx-auto px-4 py-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <i class="fas fa-robot text-white"></i>
                        </div>
                        <div>
                            <h1 class="text-xl font-bold">{name}</h1>
                            <p class="text-sm text-gray-400">{{{{ config.description }}}}</p>
                        </div>
                    </div>
                    <span class="px-3 py-1 bg-green-600/20 text-green-400 rounded-full text-sm">
                        <i class="fas fa-circle text-xs mr-1"></i> Online
                    </span>
                </div>
            </div>
        </header>

        <!-- Chat Container -->
        <main class="flex-1 max-w-4xl w-full mx-auto p-4">
            <div class="bg-gray-800 rounded-lg shadow-xl h-[600px] flex flex-col">
                <!-- Messages -->
                <div class="flex-1 overflow-y-auto p-4 space-y-4" id="messages">
                    <div class="text-center text-gray-500 py-8">
                        <i class="fas fa-comments text-4xl mb-3"></i>
                        <p>Inicie uma conversa com o agente {name}</p>
                    </div>
                    <template x-for="message in messages" :key="message.id">
                        <div :class="message.role === 'user' ? 'flex justify-end' : 'flex justify-start'">
                            <div :class="message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-100'"
                                 class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg shadow">
                                <p class="text-sm" x-text="message.content"></p>
                                <p class="text-xs mt-1 opacity-70" x-text="message.time"></p>
                            </div>
                        </div>
                    </template>
                    <div x-show="loading" class="flex justify-start">
                        <div class="bg-gray-700 px-4 py-2 rounded-lg">
                            <div class="flex space-x-2">
                                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Input -->
                <div class="border-t border-gray-700 p-4">
                    <form @submit.prevent="sendMessage" class="flex space-x-2">
                        <input 
                            x-model="newMessage"
                            type="text"
                            placeholder="Digite sua mensagem..."
                            class="flex-1 bg-gray-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            :disabled="loading"
                        >
                        <button 
                            type="submit"
                            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition duration-200 disabled:opacity-50"
                            :disabled="loading || !newMessage.trim()"
                        >
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </form>
                </div>
            </div>
        </main>
    </div>

    <script>
        function chatApp() {{
            return {{
                messages: [],
                newMessage: '',
                loading: false,
                
                async sendMessage() {{
                    if (!this.newMessage.trim()) return;
                    
                    const userMessage = {{
                        id: Date.now(),
                        role: 'user',
                        content: this.newMessage,
                        time: new Date().toLocaleTimeString('pt-BR', {{ hour: '2-digit', minute: '2-digit' }})
                    }};
                    
                    this.messages.push(userMessage);
                    this.newMessage = '';
                    this.loading = true;
                    
                    try {{
                        const response = await fetch('/chat', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ message: userMessage.content }})
                        }});
                        
                        const data = await response.json();
                        
                        this.messages.push({{
                            id: Date.now() + 1,
                            role: 'assistant',
                            content: data.response,
                            time: new Date().toLocaleTimeString('pt-BR', {{ hour: '2-digit', minute: '2-digit' }})
                        }});
                    }} catch (error) {{
                        console.error('Erro:', error);
                        this.messages.push({{
                            id: Date.now() + 1,
                            role: 'assistant',
                            content: 'Desculpe, ocorreu um erro ao processar sua mensagem.',
                            time: new Date().toLocaleTimeString('pt-BR', {{ hour: '2-digit', minute: '2-digit' }})
                        }});
                    }} finally {{
                        this.loading = false;
                        this.$nextTick(() => {{
                            const messagesEl = document.getElementById('messages');
                            messagesEl.scrollTop = messagesEl.scrollHeight;
                        }});
                    }}
                }}
            }}
        }}
    </script>
</body>
</html>'''
        
        with open(path / 'templates' / 'index.html', 'w') as f:
            f.write(html_content)

    def _create_requirements_txt(self, path: Path):
        """Cria o arquivo requirements.txt"""
        requirements = '''flask==3.0.0
anthropic==0.34.2
python-dotenv==1.0.0
gunicorn==21.2.0'''
        
        with open(path / 'requirements.txt', 'w') as f:
            f.write(requirements)

    def _create_env_file(self, path: Path):
        """Cria o arquivo .env copiando a API key existente"""
        env_content = f'ANTHROPIC_API_KEY={self.api_key}'
        
        with open(path / '.env', 'w') as f:
            f.write(env_content)

    def _create_dockerfile(self, path: Path, name: str):
        """Cria o Dockerfile"""
        dockerfile_content = f'''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]'''
        
        with open(path / 'Dockerfile', 'w') as f:
            f.write(dockerfile_content)

    def _create_landing_page(self, path: Path, name: str, agent_type: str):
        """Cria uma landing page profissional para venda do agente"""
        template = self.agent_templates.get(agent_type, self.agent_templates['conversational'])
        
        # Preços sugeridos baseados no tipo
        pricing = {
            'conversational': 'R$ 97',
            'legal': 'R$ 497',
            'medical': 'R$ 397',
            'developer': 'R$ 297',
            'data_analyst': 'R$ 397',
            'creative': 'R$ 197',
            'educator': 'R$ 297',
            'financial': 'R$ 497'
        }
        
        price = pricing.get(agent_type, 'R$ 197')
        
        landing_content = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Seu Assistente IA {template["label"]} Pessoal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-gray-900 text-white">
    <!-- Hero Section -->
    <section class="relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-purple-600/20"></div>
        <div class="relative max-w-7xl mx-auto px-4 py-24">
            <div class="text-center">
                <div class="inline-flex items-center px-4 py-2 bg-green-500/20 rounded-full mb-6">
                    <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></span>
                    <span class="text-green-400 text-sm font-medium">Disponível Agora</span>
                </div>
                <h1 class="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                    {name}
                </h1>
                <p class="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
                    {template["description"]} powered by Claude 3.5 Sonnet - A IA mais avançada da Anthropic
                </p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="#comprar" class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all transform hover:scale-105 shadow-xl">
                        <i class="fas fa-rocket mr-2"></i> Adquirir Agora por {price}
                    </a>
                    <a href="#demo" class="bg-gray-800 hover:bg-gray-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-all border border-gray-700">
                        <i class="fas fa-play mr-2"></i> Ver Demonstração
                    </a>
                </div>
            </div>
        </div>
        <!-- Animated background elements -->
        <div class="absolute top-20 left-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-pulse"></div>
        <div class="absolute bottom-20 right-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-pulse"></div>
    </section>

    <!-- Features Section -->
    <section class="py-20 bg-gray-800/50">
        <div class="max-w-7xl mx-auto px-4">
            <h2 class="text-4xl font-bold text-center mb-16">Por que escolher {name}?</h2>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-gray-800 p-8 rounded-xl border border-gray-700 hover:border-purple-500 transition-all">
                    <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-brain text-2xl"></i>
                    </div>
                    <h3 class="text-2xl font-bold mb-4">IA de Última Geração</h3>
                    <p class="text-gray-400">Powered by Claude 3.5 Sonnet, o modelo mais avançado da Anthropic com capacidades excepcionais</p>
                </div>
                <div class="bg-gray-800 p-8 rounded-xl border border-gray-700 hover:border-purple-500 transition-all">
                    <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-teal-600 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-bolt text-2xl"></i>
                    </div>
                    <h3 class="text-2xl font-bold mb-4">Instalação em 2 Minutos</h3>
                    <p class="text-gray-400">Setup simplificado com documentação clara. Funciona em qualquer dispositivo com Python</p>
                </div>
                <div class="bg-gray-800 p-8 rounded-xl border border-gray-700 hover:border-purple-500 transition-all">
                    <div class="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-shield-alt text-2xl"></i>
                    </div>
                    <h3 class="text-2xl font-bold mb-4">100% Privado e Seguro</h3>
                    <p class="text-gray-400">Rode localmente com sua própria API key. Seus dados nunca saem do seu controle</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Specific Features -->
    <section class="py-20">
        <div class="max-w-7xl mx-auto px-4">
            <div class="grid md:grid-cols-2 gap-12 items-center">
                <div>
                    <h2 class="text-4xl font-bold mb-6">Especializado em {template["label"]}</h2>
                    <div class="space-y-4">
                        <div class="flex items-start">
                            <i class="fas fa-check-circle text-green-500 mt-1 mr-3"></i>
                            <div>
                                <h4 class="font-bold mb-1">Respostas Especializadas</h4>
                                <p class="text-gray-400">Treinado especificamente para {template["label"].lower()} com conhecimento profundo</p>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <i class="fas fa-check-circle text-green-500 mt-1 mr-3"></i>
                            <div>
                                <h4 class="font-bold mb-1">Interface Intuitiva</h4>
                                <p class="text-gray-400">Chat moderno e responsivo que funciona em qualquer dispositivo</p>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <i class="fas fa-check-circle text-green-500 mt-1 mr-3"></i>
                            <div>
                                <h4 class="font-bold mb-1">Atualizações Vitalícias</h4>
                                <p class="text-gray-400">Receba melhorias e novos recursos sem custo adicional</p>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <i class="fas fa-check-circle text-green-500 mt-1 mr-3"></i>
                            <div>
                                <h4 class="font-bold mb-1">Suporte Dedicado</h4>
                                <p class="text-gray-400">Equipe pronta para ajudar com instalação e dúvidas</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="relative">
                    <div class="bg-gray-800 rounded-xl p-8 border border-gray-700 shadow-2xl">
                        <div class="aspect-video bg-gray-900 rounded-lg flex items-center justify-center">
                            <i class="fas fa-play-circle text-6xl text-gray-600"></i>
                        </div>
                    </div>
                    <div class="absolute -bottom-4 -right-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-full font-bold">
                        Demo Interativa
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section id="comprar" class="py-20 bg-gray-800/50">
        <div class="max-w-4xl mx-auto px-4">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold mb-4">Oferta Especial de Lançamento</h2>
                <p class="text-xl text-gray-400">Garanta seu agente IA pessoal hoje mesmo</p>
            </div>
            
            <div class="bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-2xl p-8 border border-purple-500/50">
                <div class="text-center">
                    <div class="text-gray-400 line-through text-2xl mb-2">De R$ {int(price.replace('R$ ', '').replace(',', '.')) * 3}</div>
                    <div class="text-6xl font-bold mb-4 bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
                        {price}
                    </div>
                    <div class="text-green-400 text-xl mb-8">Economize {int(price.replace('R$ ', '').replace(',', '.')) * 2} reais!</div>
                    
                    <div class="space-y-4 mb-8">
                        <div class="flex items-center justify-center">
                            <i class="fas fa-check text-green-500 mr-3"></i>
                            <span>Licença Vitalícia</span>
                        </div>
                        <div class="flex items-center justify-center">
                            <i class="fas fa-check text-green-500 mr-3"></i>
                            <span>Instalação Ilimitada</span>
                        </div>
                        <div class="flex items-center justify-center">
                            <i class="fas fa-check text-green-500 mr-3"></i>
                            <span>Suporte por 1 Ano</span>
                        </div>
                        <div class="flex items-center justify-center">
                            <i class="fas fa-check text-green-500 mr-3"></i>
                            <span>Atualizações Gratuitas</span>
                        </div>
                    </div>
                    
                    <button class="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-bold py-4 px-8 rounded-lg text-xl transition-all transform hover:scale-105 shadow-xl">
                        <i class="fas fa-shopping-cart mr-2"></i> Comprar Agora com Desconto
                    </button>
                    
                    <div class="mt-6 flex justify-center space-x-4">
                        <img src="https://img.shields.io/badge/Pix-Aceito-green?style=flat-square" alt="Pix">
                        <img src="https://img.shields.io/badge/Cartão-Aceito-blue?style=flat-square" alt="Cartão">
                        <img src="https://img.shields.io/badge/Boleto-Aceito-orange?style=flat-square" alt="Boleto">
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-8">
                <p class="text-gray-400">
                    <i class="fas fa-lock mr-2"></i> Pagamento 100% Seguro
                </p>
            </div>
        </div>
    </section>

    <!-- FAQ Section -->
    <section class="py-20">
        <div class="max-w-4xl mx-auto px-4">
            <h2 class="text-4xl font-bold text-center mb-12">Perguntas Frequentes</h2>
            <div class="space-y-4" x-data="{{ activeAccordion: null }}">
                <div class="bg-gray-800 rounded-lg border border-gray-700">
                    <button @click="activeAccordion = activeAccordion === 1 ? null : 1" 
                            class="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-750 transition-colors">
                        <span class="font-bold">Como faço para instalar?</span>
                        <i class="fas fa-chevron-down transition-transform" :class="activeAccordion === 1 && 'rotate-180'"></i>
                    </button>
                    <div x-show="activeAccordion === 1" x-collapse class="px-6 pb-4 text-gray-400">
                        Após a compra, você receberá um arquivo ZIP com instruções detalhadas. Basta extrair, instalar Python, e executar o comando de instalação. Leva menos de 2 minutos!
                    </div>
                </div>
                
                <div class="bg-gray-800 rounded-lg border border-gray-700">
                    <button @click="activeAccordion = activeAccordion === 2 ? null : 2" 
                            class="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-750 transition-colors">
                        <span class="font-bold">Preciso pagar mensalidade?</span>
                        <i class="fas fa-chevron-down transition-transform" :class="activeAccordion === 2 && 'rotate-180'"></i>
                    </button>
                    <div x-show="activeAccordion === 2" x-collapse class="px-6 pb-4 text-gray-400">
                        Não! O pagamento é único e você tem acesso vitalício. Você só precisa ter sua própria API key da Anthropic (instruções incluídas).
                    </div>
                </div>
                
                <div class="bg-gray-800 rounded-lg border border-gray-700">
                    <button @click="activeAccordion = activeAccordion === 3 ? null : 3" 
                            class="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-750 transition-colors">
                        <span class="font-bold">Funciona em qualquer computador?</span>
                        <i class="fas fa-chevron-down transition-transform" :class="activeAccordion === 3 && 'rotate-180'"></i>
                    </button>
                    <div x-show="activeAccordion === 3" x-collapse class="px-6 pb-4 text-gray-400">
                        Sim! Funciona em Windows, Mac e Linux. Você só precisa ter Python instalado (gratuito) e uma conexão com internet.
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 py-12 border-t border-gray-800">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <p class="text-gray-400">© 2024 {name}. Todos os direitos reservados.</p>
            <p class="text-gray-500 text-sm mt-2">Powered by Claude 3.5 Sonnet | Anthropic</p>
        </div>
    </footer>

    <script>
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
    </script>
</body>
</html>'''
        
        with open(path / 'landing_page.html', 'w') as f:
            f.write(landing_content)
        
        print(f"  ✨ Landing page criada: {path / 'landing_page.html'}")

    def _create_readme(self, path: Path, name: str, agent_type: str):
        """Cria o README.md com documentação completa"""
        template = self.agent_templates.get(agent_type, self.agent_templates['conversational'])
        
        readme_content = f'''# {name} - Agente IA {template["label"]}

## Descrição
{template["description"]}

## Instalação

### Requisitos
- Python 3.8+
- pip

### Passos

1. Clone ou extraia o agente:
```bash
cd {name}
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure sua API Key:
   - Abra o arquivo `.env`
   - Substitua o valor de `ANTHROPIC_API_KEY` pela sua chave

## Uso

### Executar localmente:
```bash
python app.py
```

Acesse: http://localhost:5000

### Docker:
```bash
docker build -t {name} .
docker run -p 5000:5000 {name}
```

## Funcionalidades
- Interface web moderna e responsiva
- Chat em tempo real com IA
- Especializado em {template["label"].lower()}
- Powered by Claude 3.5 Sonnet

## Personalização
Você pode modificar o comportamento do agente editando o `SYSTEM_PROMPT` em `app.py`.

## Suporte
Para dúvidas ou problemas, entre em contato com o desenvolvedor.
'''
        
        with open(path / 'README.md', 'w') as f:
            f.write(readme_content)

    def create_agent_zip(self, agent_path: Path) -> str:
        """Cria um arquivo ZIP do agente"""
        agent_name = agent_path.name
        zip_filename = f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(agent_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(agent_path.parent)
                    zipf.write(file_path, arcname)
        
        return zip_filename

    def review_agent(self, agent_path: Path) -> Dict[str, any]:
        """Revisa um agente criado usando IA"""
        files_to_review = ['app.py', 'templates/index.html', 'requirements.txt', 'landing_page.html']  # Adicionada landing page
        review_results = {}
        
        for file in files_to_review:
            file_path = agent_path / file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Usa Claude para revisar o código
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{
                        "role": "user",
                        "content": f"Revise este arquivo ({file}) e sugira melhorias de segurança, performance ou usabilidade:\n\n{content[:1000]}..."
                    }]
                )
                
                review_results[file] = response.content[0].text
        
        return review_results

    def create_agent_interactive(self):
        """Interface interativa para criar agentes"""
        print("=== META-AGENT: Gerador de Agentes IA ===\n")
        
        # Nome do agente
        agent_name = input("Nome do agente: ").strip().replace(' ', '_').lower()
        
        # Tipo do agente
        print("\nTipos disponíveis:")
        for key, value in self.agent_templates.items():
            print(f"  {key}: {value['label']} - {value['description']}")
        
        agent_type = input("\nEscolha o tipo (ou 'custom' para personalizado): ").strip()
        
        # Prompt customizado
        custom_prompt = None
        if agent_type == 'custom' or agent_type not in self.agent_templates:
            custom_prompt = input("\nDigite o system prompt customizado: ").strip()
            if agent_type == 'custom':
                agent_type = 'conversational'  # Usa base conversacional
        
        # Gera o agente
        print(f"\n🚀 Gerando agente '{agent_name}'...")
        agent_path = self.generate_agent_structure(agent_name, agent_type, custom_prompt)
        
        # Revisão opcional
        if input("\nDeseja que eu revise o agente criado? (s/n): ").lower() == 's':
            print("\n🔍 Revisando agente...")
            reviews = self.review_agent(agent_path)
            for file, review in reviews.items():
                print(f"\n📄 {file}:")
                print(review[:500] + "..." if len(review) > 500 else review)
        
        # Criar ZIP
        if input("\nDeseja criar um ZIP do agente? (s/n): ").lower() == 's':
            zip_file = self.create_agent_zip(agent_path)
            print(f"\n✅ ZIP criado: {zip_file}")
        
        print(f"\n✨ Agente '{agent_name}' criado com sucesso em: {agent_path}")
        print("\n📋 Arquivos gerados:")
        print(f"  - app.py (backend Flask)")
        print(f"  - index.html (interface do agente)")
        print(f"  - landing_page.html (página de vendas)")
        print(f"  - README.md (documentação)")
        print(f"  - Dockerfile (para deploy)")
        print("\nPara executar:")
        print(f"  cd {agent_path}")
        print("  python app.py")
        print("\nPara ver a landing page:")
        print(f"  Abra o arquivo: {agent_path}/landing_page.html")

    def batch_create_agents(self, agents_config: List[Dict]):
        """Cria múltiplos agentes em lote"""
        created_agents = []
        
        for config in agents_config:
            name = config.get('name')
            agent_type = config.get('type', 'conversational')
            custom_prompt = config.get('custom_prompt')
            
            print(f"Criando agente: {name}...")
            agent_path = self.generate_agent_structure(name, agent_type, custom_prompt)
            
            if config.get('create_zip', False):
                zip_file = self.create_agent_zip(agent_path)
                created_agents.append({'path': agent_path, 'zip': zip_file})
            else:
                created_agents.append({'path': agent_path})
        
        return created_agents

if __name__ == "__main__":
    meta_agent = MetaAgent()
    
    # Modo autônomo por padrão
    if len(sys.argv) == 1:
        # Cria um agente aleatório autonomamente
        agent_type = random.choice(list(meta_agent.agent_templates.keys()))
        meta_agent.autonomous_create_agent(agent_type)
    
    # Modo interativo legacy
    elif sys.argv[1] == '--interactive':
        meta_agent.create_agent_interactive()
    
    # Modo batch autônomo
    elif sys.argv[1] == '--batch':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        meta_agent.autonomous_batch_create(count)
    
    # Criar agente específico autonomamente
    elif sys.argv[1] == '--type':
        if len(sys.argv) > 2 and sys.argv[2] in meta_agent.agent_templates:
            meta_agent.autonomous_create_agent(sys.argv[2])
        else:
            print("Tipos disponíveis:")
            for key in meta_agent.agent_templates:
                print(f"  - {key}")
    
    # Modo servidor - cria agentes continuamente
    elif sys.argv[1] == '--server':
        print("🔄 Modo servidor: criando agentes continuamente...")
        print("Pressione Ctrl+C para parar\n")
        
        try:
            while True:
                # Cria um agente aleatório
                agent_type = random.choice(list(meta_agent.agent_templates.keys()))
                meta_agent.autonomous_create_agent(agent_type)
                
                # Aguarda antes de criar o próximo
                wait_time = random.randint(30, 120)
                print(f"\n⏳ Aguardando {wait_time} segundos antes do próximo agente...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            print("\n\n👋 Servidor de criação de agentes finalizado!")
    
    else:
        print("Uso:")
        print("  python meta-agent.py                    # Cria um agente autônomo aleatório")
        print("  python meta-agent.py --type [tipo]      # Cria agente específico")
        print("  python meta-agent.py --batch [qtd]      # Cria múltiplos agentes")
        print("  python meta-agent.py --server           # Modo servidor contínuo")
        print("  python meta-agent.py --interactive      # Modo interativo (legacy)")