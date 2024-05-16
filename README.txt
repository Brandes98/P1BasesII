SISTEMA DE ENCUESTAS - PROYECTO DE BASES II
------------------------------------------------------------------
En el siguiente proyecto se logrará visualizar un sistema donde le
permitirá a los usuarios crear, publicar y gestionar encuestas con 
diferentes tipos de preguntas, así como registrar y administrar 
listas de encuestas. 

El siguiente proyecto fue realizado por: 
	● Brandon Calderón Cubero 
	● Ian Coto Soto 
	● Esteban Villavicencio Soto
	● Mauricio Campos Cerdas


A continuación se brindará una serie de instrucciones de cómo uti-
lizar el sistema de encuestas. Se solicita al lector seguir cuida-
dosamente cada instrucción para que así tenga éxito en su instala-
ción y posteriormente su uso. 


PREÁMBULO
	1. Instalar la aplicación Docker Desktop. 
	2. Iniciar sesión y/o registrarse en la aplicación Docker Desktop.
	3. Instalar la aplicación de Visual Studio Code. 


1. INICIALIZACIÓN DE DOCKER E INSTALACIÓN DEL SISTEMA EN EL MISMO
	1.1 Abrir la aplicación de Docker Desktop. 
	1.2 Abrir la aplicación de Visual Studio Code. 
	1.3 En la aplicación de Visual Studio Code dirigirse a la sección de 
	    "File" y seleccionar la opción de "Open Folder" y selecciona la 
	    carpeta que tiene el sistema de encuestas, es decir, la carpeta
	    con el nombre de "P1BasesII-Ian".
	1.4 Una vez abierto la carpeta, proceda a dirigirse al apartado de 
	    "Terminal" y selecciona la opción de "New Terminal". 
	1.5 Dirígase a la nueva terminal creada y coloque el siguiente comando:
	    "docker compose up" y presiona la tecla enter. De esta manera la 
	    API comenzaría a funcionar. 


2. USO CON POSTMAN
	2.1 Instalar la aplicación de Postman e iniciar sesión y/o registrarse. 
	2.2 Abrir la aplicación de Postman y dirigirse a la opción de "Importar" 
	    y seleccionar el archivo "BDII-Proyecto1.postman_collection.json" y 
	    presiona el botón de aceptar para que así se carguen las pruebas 
	    realizadas.
	2.3 Una vez cargadas las pruebas, seleccione la prueba que desea ejecutar
	    y presiona el botón "Send" para que así pueda visualizar el resultado 
	    de la prueba.


3. EJECUCIÓN DE LAS PRUEBAS UNITARIAS 
	3.1 Abra la aplicación de Visual Studio Code y proceda a dirigirse al apar-
	    tado de "Terminal" y selecciona la opción de "New Terminal". Nota: Si 
	    se encuentra en la ventanda de Visual Studio Code del paso #1, es im-
	    portante que no realice ninguna acción en la terminal de este paso, si-
	    no que abra una nueva terminal para este paso. 
	3.2 Una vez en la terminal ejecute el siguiente comando: 
	    docker-compose exec app poetry run (inserte el nombre completo del archivo de la prueba a ejecutar)
	    y presione el botón de enter. 
	3.3 Poco después de presionar el botón, podrá observar la ejecución de las 
	    pruebas y verá que la evaluación realiza por el Pytest es del 100% de 
	    aceptación.














