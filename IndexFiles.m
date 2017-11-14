
ds = dir('dataset/clip07/img/*/*.jpg');
fid = fopen('dataset/index_clip07.txt', 'w');

for n = 1:numel(ds)   
    org_file = strcat(ds(n).folder, '\', ds(n).name);
    %xml_file = regexprep(org_file, '\\img\\[0-9]\\', '\\ano\\');
    xml_file = regexprep(org_file, '\\img\\', '\\ano\\');
    xml_file = replace(xml_file, '.jpg', '.xml');
    
    disp(xml_file);
    fprintf(fid, '%s %s\r\n', org_file, xml_file);
end

fclose(fid);