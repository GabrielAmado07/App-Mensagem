class No:

    def __init__(self, valor):
        self.valor = valor
        self.esquerda = None
        self.direita = None


class Arvore:

    def __init__(self):
        self.raiz = None
        self.nos = []

    def inserir(self, valor):

        novo_no = No(valor)

        self.nos.append(novo_no)

        if self.raiz is None:
            self.raiz = novo_no
            return

        fila = [self.raiz]

        while fila:

            atual = fila.pop(0)

            if atual.esquerda is None:
                atual.esquerda = novo_no
                return
            else:
                fila.append(atual.esquerda)

            if atual.direita is None:
                atual.direita = novo_no
                return
            else:
                fila.append(atual.direita)

    def pre_ordem(self, no):

        if no is None:
            return ""

        resultado = no.valor

        resultado += self.pre_ordem(no.esquerda)

        resultado += self.pre_ordem(no.direita)

        return resultado

    def descriptografar(self, mensagem):

        arvore = Arvore()

        # Recria a mesma estrutura da árvore
        for caractere in mensagem:
            arvore.inserir("")

        # Guarda os nós na ordem de pré-ordem
        nos_pre_ordem = []

        def percorrer(no):

            if no is None:
                return

            nos_pre_ordem.append(no)

            percorrer(no.esquerda)

            percorrer(no.direita)

        percorrer(arvore.raiz)

        # Coloca a mensagem criptografada
        # nos nós seguindo a pré-ordem
        for i in range(len(mensagem)):
            nos_pre_ordem[i].valor = mensagem[i]

        # Recupera os caracteres na ordem
        # original da árvore
        resultado = ""

        for no in arvore.nos:
            resultado += no.valor

        return resultado
