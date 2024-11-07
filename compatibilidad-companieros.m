% crear matriz de numeros aleatorios para el ejercicio.
Encuesta = round(10*rand(40,5));
% Filas = Inquilinos, Columnas = Preferencias
Inquilinos = size(Encuesta,1);
Preferencias = size(Encuesta,2);

% matriz de incompatibilidad
Incompatibilidad = zeros(Inquilinos,Inquilinos);


for i=1:Inquilinos-1
    for j=1:Inquilinos-1
        for k= 1:Preferencias
            r(k)=(Encuesta(i,k)-Encuesta(j+1,k))^2;
        end
        q(i)=sum(r);
        Incompatibilidad(i,j+1)=round(sqrt(q(i)));
        Incompatibilidad(j+1,i)=round(sqrt(q(i)));
    end
end
clear i j k

% quiero ver con quienes tiene mejor compatibilidad el inquilino X
X = input('Por favor ingrese el numero de un inquilino: ');

% tomo la columna del inquilino
Vecinos = Incompatibilidad(:,X);

% agrego al principio una columna con el numero de inquilino
Vecinos = [(1:length(Vecinos))',Vecinos];

% ordeno de menor a mayor según la columna 2
Vecinos = sortrows(Vecinos, 2);

% convierto la variable a palabra
Vec1 = num2str(Vecinos(2,1));
Vec2 = num2str(Vecinos(3,1));
Vec3 = num2str(Vecinos(4,1));

fprintf('Los tres vecinos más compatibles con el inquilino solicitado son: %s, %s y %s\n', Vec1, Vec2, Vec3);
