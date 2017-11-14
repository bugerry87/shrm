
colors = [ ...
    0 0 1; ...
    0 .5 1; ...
    0 1 0; ...
    0 1 1; ...
    1 0 0; ...
    1 0 .5; ...
    1 0 1; ...
    1 1 0; ...
    1 1 1 ...
    ];

ds = dir('dataset/clip01/img/*/*.jpg');

for k = 1:numel(ds)
    disp(ds(k).name);
    imgfile = strcat(ds(k).folder, '\', ds(k).name);
    %xmlfile = regexprep(imgfile, '\\img\\[0-9]\\', '\\ano\\');
    xmlfile = replace(imgfile, '\img\', '\ano\');
    xmlfile = replace(xmlfile, '.jpg', '.xml');
    I = imread(imgfile);
    X = parseXML(xmlfile);
    
    figure(1)
    imshow(I)
    hold on
    for n = 1:numel(X.Children)
        if strcmp(X.Children(n).Name, 'object')
            object = X.Children(n);
        else
            continue;
        end
        
        for m = 1:numel(object.Children)
            if strcmp(object.Children(m).Name, 'id')
                id = str2num(object.Children(m).Children.Data);
            elseif strcmp(object.Children(m).Name, 'name')
                name = replace(object.Children(m).Children.Data, '_', ' ');
            elseif strcmp(object.Children(m).Name, 'bndbox')
                bndbox = object.Children(m);
            else
                continue;
            end
        end
        
        if id == 4
            continue;
        end
        
        for m = 1:numel(bndbox.Children)
            if strcmp(bndbox.Children(m).Name, 'xmin')
                xmin = str2num(bndbox.Children(m).Children.Data);
            elseif strcmp(bndbox.Children(m).Name, 'ymin')
                ymin = str2num(bndbox.Children(m).Children.Data);
            elseif strcmp(bndbox.Children(m).Name, 'xmax')
                xmax = str2num(bndbox.Children(m).Children.Data);
            elseif strcmp(bndbox.Children(m).Name, 'ymax')
                ymax = str2num(bndbox.Children(m).Children.Data);
            else
                continue;
            end
        end
        
        roi = [xmin, ymin, xmax - xmin, ymax - ymin];    
        rectangle('Position', roi, 'EdgeColor', colors(id, :), 'LineWidth', 3);
        text(xmin, ymin, name, 'FontSize', 8, 'BackgroundColor', colors(id, :), 'VerticalAlignment', 'top');
    end
    hold off
    pause;
end