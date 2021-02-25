import csv
import numpy as np


class Station:  # Classe que nos cria objetos do tipo estação de metro

    def __init__(self, id, latitude, longitude, name, display_name, zone, total_lines, rails):
        self._id = id
        self._latitude = latitude
        self._longitude = longitude
        self._name = name
        self._display_name = display_name  # Este objeto tem como caracteristica o id, latitude, longitude, name, display_name, zone, total_lines, rails
        self._zone = zone
        self._total_lines = total_lines
        self._rails = rails

    def get_id(self):  # Retorna o id da estação
        return self._id

    def get_name(self):
        return self._name


class Edge_line:  # Classe que nos cria objetos do tipo conexão de metro

    def __init__(self, u, v, line, time):
        self._origin = u
        self._destination = v  # Este objeto é constituido pelos atributos origem da conexão, destino da conexão, tempo entre as linhas de conexão
        self._line = line
        self._time = time

    def endpoints(self):  # Retorna um tuplo com a origem e destino da conexão
        return self._origin, self._destination

    def opposite(self, v):  # Dando como input a origem ou o destino, devolve o oposto do input
        if v is self._destination:
            return self._origin
        else:
            return self._destination

    def get_line(self):  # Retorna a que linha pertence esta conexão
        return self._line

    def get_time(self):  # Retorna o tempo entre a origem e o destino
        return self._time


stations = []  # Lista que vai guardar as estações
connections = []  # Lista que vai guardar as conexões
with open("london.stations.txt") as csv_file:  # Leitura do ficheiro das estações
    csv_reader = csv.DictReader(csv_file)
    z = 0
    dic1 = {}  # Criar um dicionário para guardar os antigos e novos ids
    for row in csv_reader:
        stations.append(
            Station(z, float(row["latitude"]), float(row["longitude"]), row["name"], row["display_name"],
                    # Vamos renomear os ids
                    float(row["zone"]), int(row["total_lines"]),
                    int(row["rail"])))  # Adiciona um objeto do tipo estação por cada iteração à lista
        dic1[int(row["id"])] = z  # T
        z += 1

with open("london.connections.txt") as csv_file2:  # Leitura do ficheiro das conexões
    csv_reader2 = csv.DictReader(csv_file2)
    for row in csv_reader2:
        connections.append(Edge_line(dic1[int(row["station1"])], dic1[int(row["station2"])], int(row["line"]),int(row["time"])))  # Adiciona um objeto do tipo estação por cada iteração à lista
                                                                                                    # E associar o novo id à conexão
dic_stations = {}  # Criação de um dicionário com o id e nome associados a cada estação
for s in stations:
    dic_stations[s.get_id()] = s.get_name()


class AdMatrix:

    def __init__(self, c):
        self._m = np.zeros([c, c])  # Criação de uma matriz com o comprimento e largura do número de estações

    def adjacency_matrix(self):  # Transformar a matriz inicial numa amtriz de adjacência
        i = 0
        while i != len(connections):
            o_and_d = connections[i].endpoints()  # Vamos iterar sobre todas as conexões e em seguida
            self._m[(o_and_d[0]), (o_and_d[1])] = 1  # vamos à entrada com a linha do id da origemm e com coluna do id do destino
            self._m[(o_and_d[1]), (o_and_d[0])] = 1  # E vice-versa
            i += 1

    def degree_matrix(self):
        mdig = np.zeros([len(stations), len(stations)])  # Criamos uma matriz para colocar os grau de conexões da estações
        for i in range(0, len(stations)):  # Percorremos a matriz de adjacência
            for j in range(0, len(stations)):
                if self._m[i, j] == 1:  # Se existir conexão entre a estação i e uma estação j
                    mdig[i, i] += 1  # Adicionamos mais 1 à posição referente à estação i
        return mdig

    def laplace(self):
        return self.degree_matrix() - self._m  # A matriz de laplace é igual à subtração matriz de graus das estações

    def spectral_bisection(self):
        eigenvalues, eigenvectors = np.linalg.eigh(l)  # Vamos achar os vetores e valores próprios da matriz próprios

        fiedler_ind = np.argsort(eigenvalues)[1]  # Vamos achar o indice correspondente ao valor de fiedler

        partition1 = []  # São criadas duas partições de forma a dividir o metro em duas partes para depois conseguirmos ver quais as conexões a cortar
        partition2 = []
        c = 0
        for i in eigenvectors[:, fiedler_ind]:  # Vamos percorrer o vetor de Fiedler que tem metade dos seus valores negativos e metade negativos
            if i >= 0:  # E por isso é nos extramamente útil para partir o metro
                partition1.append(c)  # Caso o valor seja maior ou igual a 0 na entrada da estação do vetor de Fiedler essa estação vai para a primera partição
            else:
                partition2.append(c)  # Caso contrário vai para a segunda partição
            c += 1
        return set(partition1), set(partition2) #Divido em duas partições

    def connections_to_cut(self):
        lista = []
        for i in spec_bis[0]:  # Percorrer as estações i na primeira partição
            for j in spec_bis[1]:  # Percorrer as estações j na segunda partição
                for con in connections:  # Percorrer todas as conexões
                    if i == con.endpoints()[0] and j == con.endpoints()[1]:  # Caso exista uma conexão entre uma estação de uma partição 1 e da partição 2 adicionamos à lista
                        lista.append((i, j))
                    elif i == con.endpoints()[1] and j == con.endpoints()[0]:  # E vice-versa (isto porque estas conexões sao as unicas que restam a ligar as duas partições)
                        lista.append((j, i))
        return lista

    def min_cut(self):

        vect_s = np.zeros([len(stations)])  # Construimos um vetor com de sinal para guardar os valores de sinal( -1 e  1)

        eigenvalues, eigenvectors = np.linalg.eigh(l)  # Vamos achar os vetores e valores próprios da matriz de laplace

        fiedler_vect = eigenvectors[:, np.argsort(eigenvalues)[1]]  # Vamos achar o vetor de fiedler

        for i in range(0, len(stations)):  # Vamos percorrer o vetor próprio de fiedler
            if fiedler_vect[i] >= 0:  # Caso o valor seja maior ou igual a 0 na entrada da estação do vetor de Fiedler vai tomar o valor de 1
                vect_s[i] = 1
            else:
                vect_s[i] = -1  # Caso contrário vai tomar -1, é uma boa maneira de separarmos quais os valores que são positivos e negativos
        return 0.25*np.dot(np.dot(vect_s.transpose(), l), vect_s)  # Segundo o teorema de Minimax de Courant Fisher 1/4*vect_s.transpose*matriz_laplace*vect_s é igaul ao corte minimo


# SCRIPT____________________________________________________________________________
m = AdMatrix(len(stations))
m.adjacency_matrix()
d = m.degree_matrix()
l = m.laplace()
spec_bis = m.spectral_bisection()
custo_minimo = m.min_cut()
conexoes_a_cortar = m.connections_to_cut()

lista_de_corte = []  # Lista para guardar os nomes das conexões que vamos cortar
for s1, s2 in m.connections_to_cut():
    lista_de_corte.append((dic_stations[s1], dic_stations[s2]))  # Tornamos os valores em nomes das estações
lista_de_corte_final = set(lista_de_corte)  # Conjunto sem repetição de conexões
