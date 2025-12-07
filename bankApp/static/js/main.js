// Fonctions globales pour l'application
class BankChatbot {
    constructor() {
        this.isInitialized = false;
    }

    initChatbot() {
        if (this.isInitialized) return;
        
        // Références aux éléments du DOM
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');

        if (!this.chatMessages) return;

        this.setupEventListeners();
        this.showWelcomeMessage();
        this.isInitialized = true;
    }

    setupEventListeners() {
        // Clic sur le bouton d'envoi
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Touche Entrée
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Focus automatique
        this.userInput.focus();
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        
        if (!message) return;
        
        // Ajout du message utilisateur
        this.addMessage(message, true);
        this.userInput.value = '';
        this.sendButton.disabled = true;
        
        // Affichage indicateur de frappe
        this.showTypingIndicator();
        
        try {
            const response = await this.callChatAPI(message);
            this.handleBotResponse(response);
            
        } catch (error) {
            console.error('Erreur:', error);
            this.handleError();
        }
        
        this.hideTypingIndicator();
        this.sendButton.disabled = false;
    }

    async callChatAPI(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }
        
        return await response.json();
    }

    handleBotResponse(data) {
        if (data.success) {
            this.addMessage(
                data.response, 
                false, 
                data.category, 
                data.confidence
            );
        } else {
            this.addMessage(
                "Désolé, une erreur s'est produite. Veuillez réessayer.", 
                false
            );
        }
    }

    handleError() {
        this.hideTypingIndicator();
        this.addMessage(
            "Je n'ai pas compris votre question, pouvez-vous reformuler ?", 
            false
        );
    }

    addMessage(message, isUser = false, category = null, confidence = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const timestamp = new Date().toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        let messageHTML = '';
        
        if (isUser) {
            // Message utilisateur - icône à droite
            messageHTML = `
                <div class="d-flex align-items-start gap-3">
                    <div class="flex-grow-1">
                        <div class="message-container">
                            <div class="message-content">
                                ${message}
                            </div>
                            <div class="message-time">
                                ${timestamp}
                            </div>
                        </div>
                    </div>
                    <div class="user-icon-message">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
            `;
        } else {
            // Message bot - icône à gauche
            messageHTML = `
                <div class="d-flex align-items-start gap-3">
                    <div class="bot-icon-message">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="message-container">
                            <div class="message-content">
                                ${message}
                            </div>
                            <div class="message-time">
                                ${timestamp}
                            </div>
            `;
            
            // Métadonnées pour les messages du bot
            if (category && confidence) {
                messageHTML += `
                    <div class="message-meta">
                        Catégorie: ${category.toUpperCase()} | Niveau de confiance: ${(confidence * 100).toFixed(0)}%
                    </div>
                `;
            }
            
            messageHTML += `
                        </div>
                    </div>
                </div>
            `;
        }
        
        messageDiv.innerHTML = messageHTML;
        this.chatMessages.appendChild(messageDiv);
        
        // Défilement automatique
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'block';
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }

    hideTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }

    showWelcomeMessage() {
        setTimeout(() => {
            this.addMessage(
                "Bonjour ! Je suis votre assistant bancaire. Posez-moi vos questions sur vos comptes, cartes, transactions, etc.", 
                false
            );
        }, 1000);
    }
}

// Initialisation globale
const chatbot = new BankChatbot();

// Fonction d'initialisation pour la page chatbot
function initChatbot() {
    chatbot.initChatbot();
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Le chatbot s'initialise automatiquement sur sa page
    if (document.getElementById('chatMessages')) {
        initChatbot();
    }
    
    // Gestion des boutons de suggestion (si présents sur la page)
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const userInput = document.getElementById('userInput');
            if (userInput) {
                userInput.value = this.textContent.trim();
                userInput.focus();
            }
        });
    });
});