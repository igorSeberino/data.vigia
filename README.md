# data.vigia

<p align="center">
  <img src=".github/assets/logo.svg" alt="vigia: engrenagem com sinal de vibração" width="160">

  <h3 align="center">vigia</h3>

  <p align="center">
    Manutenção preditiva de uma máquina de usinagem na Indústria 4.0
  </p>
</p>

<p align="center">
  <a href="https://github.com/igorSeberino/data.vigia/actions/workflows/ci.yml"><img src="https://github.com/igorSeberino/data.vigia/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://doi.org/10.24432/C5HS5C"><img src="https://img.shields.io/badge/dados-AI4I%202020%20(UCI)-2BB3A3" alt="Dados: AI4I 2020 (UCI)"></a>
</p>

O **vigia** prevê, a partir das leituras de sensores de uma máquina de usinagem (temperaturas,
rotação, torque e desgaste da ferramenta), se um ciclo de processo vai falhar, e mede quanto
isso economiza frente às manutenções corretiva e preventiva. O trabalho passa por todo o ciclo
de ciência de dados: coleta e validação dos dados, modelo dimensional em SQLite, análise
exploratória com testes estatísticos, modelos de classificação e análise de custo.

> Projeto acadêmico — disciplina de Ciência de Dados, Prof. Claudinei Dias (Ney), Engenharia de Software, Centro Universitário Católica de Santa Catarina.

**Integrantes:** Adrian Cesar Gonçalves (@adrian-cesar) · Gabriel Carvalho (@gabrielcarvallho) ·
Igor Thiago Seberino (@igorSeberino) · Renato Colin Neto (@rcolinneto)

Este README é o relatório completo do trabalho. Backlog e andamento no Project
[**@vigia**](https://github.com/users/igorSeberino/projects/2); plano e divisão de tarefas em
[`docs/plano/`](docs/plano/).

| Notebook | Conteúdo |
|---|---|
| [01 – Coleta e preparação](notebooks/01_coleta_e_preparacao.ipynb) | origem, validação, atributos físicos, divisão |
| [02 – Modelo de dados (SQL)](notebooks/02_modelo_de_dados_sql.ipynb) | esquema estrela em SQLite e consultas |
| [03 – Análise exploratória](notebooks/03_analise_exploratoria.ipynb) | distribuições, testes estatísticos, regras físicas |
| [04 – Modelagem preditiva](notebooks/04_modelagem_preditiva.ipynb) | comparação, ajuste e avaliação dos modelos |
| [05 – Impacto no negócio](notebooks/05_impacto_no_negocio.ipynb) | custo, limiar ótimo, estratégias de manutenção |

## 1. Introdução
### 1.1 A Indústria 4.0 e sua importância
<!-- RESPONSÁVEL: @adrian-cesar · T5 -->
O termo *Industrie 4.0* nasceu de uma iniciativa estratégica do governo alemão para manter a
competitividade da sua indústria. Em 2013, o grupo de trabalho da iniciativa publicou as
recomendações para implantá-la, descrevendo a fábrica do futuro como uma rede de máquinas,
produtos e sistemas que trocam informação e se coordenam de forma autônoma (KAGERMANN;
WAHLSTER; HELBIG, 2013). A ideia é tratada como a quarta revolução industrial, depois da
mecanização, da produção em massa e da automação eletrônica.

A base técnica dessa transformação são os sistemas ciberfísicos: equipamentos físicos com
sensores e capacidade de processamento, ligados entre si pela Internet das Coisas industrial.
Sobre essa base atuam o big data e a análise de dados, a computação em nuvem e a integração
vertical (do chão de fábrica à gestão) e horizontal (entre empresas da cadeia) (LEE; BAGHERI;
KAO, 2015).

A importância da Indústria 4.0 está no ganho de produtividade, qualidade e flexibilidade e,
principalmente, na troca de decisões tomadas por experiência por decisões orientadas por
dados. No Brasil, a Confederação Nacional da Indústria aponta a adoção dessas tecnologias como
condição para a competitividade da indústria nacional e propõe uma agenda com sete dimensões
prioritárias, da formação de pessoas à infraestrutura de banda larga (CNI, 2016).

A ciência de dados é o elo entre o sensor e a decisão: transforma leituras brutas em
informação útil para a operação. Entre as suas aplicações industriais, a manutenção preditiva
é uma das mais estudadas (ZONTA *et al.*, 2020; CARVALHO *et al.*, 2019), e é o tema deste
trabalho.

### 1.2 Definição do problema
<!-- RESPONSÁVEL: @adrian-cesar · T5 -->
A manutenção de equipamentos segue três estratégias. Na corretiva, o equipamento é consertado
depois que falha. Na preventiva, a intervenção ocorre em intervalos fixos de tempo ou de uso,
falhe o equipamento ou não. Na preditiva, a intervenção é decidida pela condição real do
equipamento, medida por dados (MOBLEY, 2002).

Cada estratégia tem um custo. A falha não planejada para a linha, gera refugo e exige reparo
urgente. A troca preventiva feita cedo demais desperdiça ferramenta ainda útil; feita tarde
demais, não evita a falha. A manutenção preditiva busca o ponto de equilíbrio: intervir só
quando os dados indicam risco.

**Problema deste trabalho:** em uma máquina de usinagem monitorada por sensores (temperatura do
ar, temperatura do processo, rotação, torque e desgaste da ferramenta), prever se um ciclo de
processo vai falhar e decidir quando intervir com o menor custo esperado. Os dados são do
conjunto AI4I 2020, publicado para reproduzir dados reais de manutenção preditiva
(MATZKA, 2020; UCI MACHINE LEARNING REPOSITORY, 2020). Por ser um conjunto sintético, os
resultados valem para a máquina simulada; essa limitação é discutida na seção 3.3.

### 1.3 Objetivos
<!-- RESPONSÁVEL: @adrian-cesar · T5 -->
**Objetivo geral:** aplicar o ciclo de ciência de dados (coleta, preparação, modelagem de
dados, análise e avaliação) para propor uma política de manutenção preditiva baseada em dados
para a máquina do conjunto AI4I 2020.

**Objetivos específicos:**

1. Coletar, validar e preparar o conjunto de dados, documentando a qualidade e as
   inconsistências.
2. Construir um modelo de dados dimensional (esquema estrela) que permita consultas analíticas
   sobre os ciclos e as falhas.
3. Caracterizar estatisticamente as variáveis associadas à falha.
4. Treinar e comparar modelos de classificação para prever a falha de um ciclo, com validação
   adequada a dados desbalanceados.
5. Estimar o impacto financeiro da manutenção preditiva frente às estratégias corretiva e
   preventiva.
6. Disponibilizar uma implementação em Python reprodutível e documentada.

## 2. Metodologia
### 2.1 Descrição dos dados (fontes, tipos, volume)
<!-- RESPONSÁVEL: @igorSeberino · T1 -->
_Em construção._

### 2.2 Coleta e preparação dos dados
<!-- RESPONSÁVEL: @igorSeberino · T1 -->
_Em construção._

### 2.3 Ferramentas e técnicas de modelagem de dados
<!-- RESPONSÁVEL: @igorSeberino · T1 (tabela de ferramentas) -->
_Em construção._

#### 2.3.1 Modelagem dimensional (esquema estrela em SQLite)
<!-- RESPONSÁVEL: @igorSeberino · T2 -->
_Em construção._

#### 2.3.2 Modelagem preditiva (aprendizado supervisionado)
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

### 2.4 Métodos de análise de dados
#### 2.4.1 Análise exploratória e testes estatísticos
<!-- RESPONSÁVEL: @adrian-cesar · T3 -->
_Em construção._

#### 2.4.2 Validação e métricas dos modelos
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

#### 2.4.3 Análise de custo e estratégias de manutenção
<!-- RESPONSÁVEL: @gabrielcarvallho · T6 -->
_Em construção._

## 3. Desenvolvimento
### 3.1 Implementação dos modelos de dados
#### 3.1.1 Modelo dimensional
<!-- RESPONSÁVEL: @igorSeberino · T2 -->
_Em construção._

#### 3.1.2 Modelos preditivos
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

### 3.2 Análise dos resultados
#### 3.2.1 O que a exploração mostrou
<!-- RESPONSÁVEL: @adrian-cesar · T3 -->
_Em construção._

#### 3.2.2 Consultas analíticas no modelo dimensional
<!-- RESPONSÁVEL: @igorSeberino · T2 -->
_Em construção._

#### 3.2.3 Desempenho dos modelos
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

#### 3.2.4 Impacto financeiro
<!-- RESPONSÁVEL: @gabrielcarvallho · T6 -->
_Em construção._

### 3.3 Discussão sobre a eficácia das soluções propostas
#### 3.3.1 Eficácia técnica e limitações do modelo
<!-- RESPONSÁVEL: @rcolinneto · T4 -->
_Em construção._

#### 3.3.2 Eficácia para o negócio
<!-- RESPONSÁVEL: @gabrielcarvallho · T6 -->
_Em construção._

### 3.4 Implementação em Python
<!-- RESPONSÁVEL: @igorSeberino · T7 -->
_Em construção._

### 3.5 Considerações finais
<!-- RESPONSÁVEL: @igorSeberino · T7 -->
_Em construção._

## 4. Referências
<!-- RESPONSÁVEL: @adrian-cesar · T5 (demais integrantes acrescentam as que citarem) -->
BREIMAN, L. Random forests. **Machine Learning**, v. 45, n. 1, p. 5-32, 2001. DOI: https://doi.org/10.1023/A:1010933404324.

CARVALHO, T. P. *et al.* A systematic literature review of machine learning methods applied to predictive maintenance. **Computers & Industrial Engineering**, v. 137, 106024, 2019. DOI: https://doi.org/10.1016/j.cie.2019.106024.

CHICCO, D.; JURMAN, G. The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation. **BMC Genomics**, v. 21, n. 1, 6, 2020. DOI: https://doi.org/10.1186/s12864-019-6413-7.

CONFEDERAÇÃO NACIONAL DA INDÚSTRIA (CNI). **Desafios para indústria 4.0 no Brasil**. Brasília: CNI, 2016. Disponível em: https://www.portaldaindustria.com.br/publicacoes/2016/8/desafios-para-industria-40-no-brasil/. Acesso em: 23 out. 2026.

FRIEDMAN, J. H. Greedy function approximation: a gradient boosting machine. **The Annals of Statistics**, v. 29, n. 5, p. 1189-1232, 2001. DOI: https://doi.org/10.1214/aos/1013203451.

HARRIS, C. R. *et al.* Array programming with NumPy. **Nature**, v. 585, n. 7825, p. 357-362, 2020. DOI: https://doi.org/10.1038/s41586-020-2649-2.

HUNTER, J. D. Matplotlib: a 2D graphics environment. **Computing in Science & Engineering**, v. 9, n. 3, p. 90-95, 2007. DOI: https://doi.org/10.1109/MCSE.2007.55.

KAGERMANN, H.; WAHLSTER, W.; HELBIG, J. **Recommendations for implementing the strategic initiative INDUSTRIE 4.0**: final report of the Industrie 4.0 Working Group. Frankfurt am Main: acatech, 2013. Disponível em: https://www.acatech.de/wp-content/uploads/2018/03/Final_report__Industrie_4.0_accessible.pdf. Acesso em: 23 out. 2026.

KIMBALL, R.; ROSS, M. **The data warehouse toolkit**: the definitive guide to dimensional modeling. 3. ed. Indianapolis: Wiley, 2013.

LEE, J.; BAGHERI, B.; KAO, H.-A. A cyber-physical systems architecture for Industry 4.0-based manufacturing systems. **Manufacturing Letters**, v. 3, p. 18-23, 2015. DOI: https://doi.org/10.1016/j.mfglet.2014.12.001.

MANN, H. B.; WHITNEY, D. R. On a test of whether one of two random variables is stochastically larger than the other. **The Annals of Mathematical Statistics**, v. 18, n. 1, p. 50-60, 1947. DOI: https://doi.org/10.1214/aoms/1177730491.

MATZKA, S. Explainable artificial intelligence for predictive maintenance applications. *In*: INTERNATIONAL CONFERENCE ON ARTIFICIAL INTELLIGENCE FOR INDUSTRIES (AI4I), 3., 2020, Irvine. **Proceedings** [...]. IEEE, 2020. p. 69-74. DOI: https://doi.org/10.1109/AI4I49448.2020.00023.

McKINNEY, W. Data structures for statistical computing in Python. *In*: PYTHON IN SCIENCE CONFERENCE, 9., 2010, Austin. **Proceedings** [...]. 2010. p. 56-61. DOI: https://doi.org/10.25080/Majora-92bf1922-00a.

MOBLEY, R. K. **An introduction to predictive maintenance**. 2. ed. Amsterdam: Butterworth-Heinemann, 2002.

PEDREGOSA, F. *et al.* Scikit-learn: machine learning in Python. **Journal of Machine Learning Research**, v. 12, p. 2825-2830, 2011. Disponível em: https://www.jmlr.org/papers/v12/pedregosa11a.html. Acesso em: 23 out. 2026.

SAITO, T.; REHMSMEIER, M. The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. **PLOS ONE**, v. 10, n. 3, e0118432, 2015. DOI: https://doi.org/10.1371/journal.pone.0118432.

SHEARER, C. The CRISP-DM model: the new blueprint for data mining. **Journal of Data Warehousing**, v. 5, n. 4, p. 13-22, 2000.

UCI MACHINE LEARNING REPOSITORY. **AI4I 2020 predictive maintenance dataset**. 2020. DOI: https://doi.org/10.24432/C5HS5C. Acesso em: 23 out. 2026.

VIRTANEN, P. *et al.* SciPy 1.0: fundamental algorithms for scientific computing in Python. **Nature Methods**, v. 17, n. 3, p. 261-272, 2020. DOI: https://doi.org/10.1038/s41592-019-0686-2.

WASKOM, M. L. seaborn: statistical data visualization. **Journal of Open Source Software**, v. 6, n. 60, 3021, 2021. DOI: https://doi.org/10.21105/joss.03021.

ZONTA, T. *et al.* Predictive maintenance in the Industry 4.0: a systematic literature review. **Computers & Industrial Engineering**, v. 150, 106889, 2020. DOI: https://doi.org/10.1016/j.cie.2020.106889.

## Contribuindo

Fluxo Trunk-Based com o time de agentes do Claude Code em [`.claude/`](.claude/README.md):
`/setup` → `/tbd-start <issue>` → implementação → `/tbd-commit` → `/tbd-pr`. Regras do projeto
em [`CLAUDE.md`](CLAUDE.md); cada PR precisa de CI verde e aprovação de outro integrante.

## Dados
Dados: *AI4I 2020 Predictive Maintenance Dataset*, UCI Machine Learning Repository,
https://doi.org/10.24432/C5HS5C, licença CC BY 4.0 (cópia em `data/raw/ai4i2020.csv`).
