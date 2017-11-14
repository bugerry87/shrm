
cm = struct( ...
    'r_arm', hex2dec('20'), ...
    'r_palm', hex2dec('40'), ...
    'r_fingertips', hex2dec('60'), ...
    'r_fingertip', hex2dec('60'), ...
    'r_thumb', hex2dec('60'), ...
    'r_index', hex2dec('80'), ...
    'r_mid', hex2dec('A0'), ...
    'r_ring', hex2dec('C0'), ...
    'r_pinky', hex2dec('E0') ...
);

ds = dir('dataset/clip01/lab/*/*.png');
limit = 24;

for n = 1:numel(ds)
    disp(ds(n).name);
    inpath = strcat(ds(n).folder, '/', ds(n).name);
    I = imread(inpath);
    Isz = size(I);
    min_ext = [int32(Isz(2) * 0.075), int32(Isz(1) * 0.075)];
    f = fieldnames(cm);
    outdir = replace(ds(n).folder, 'lab', 'ano');
    outfile = replace(ds(n).name, '.png', '.xml');
    
    if exist(outdir, 'file') ~= 7
        mkdir(outdir);
    end
    
    doc = com.mathworks.xml.XMLUtils.createDocument('annotation');
    anno = doc.getDocumentElement;
    node = doc.createElement('folder');
    node.appendChild(doc.createTextNode(ds(n).folder));
    anno.appendChild(node);
    
    node = doc.createElement('filename');
    node.appendChild(doc.createTextNode(ds(n).name));
    anno.appendChild(node);
    
    size_n = doc.createElement('size');    
    node = doc.createElement('width');
    node.appendChild(doc.createTextNode(num2str(Isz(2))));
    size_n.appendChild(node); 
    
    node = doc.createElement('height');
    node.appendChild(doc.createTextNode(num2str(Isz(1))));
    size_n.appendChild(node); 
    
    node = doc.createElement('depth');
    if numel(Isz) >= 3
        node.appendChild(doc.createTextNode(num2str(Isz(3))));
    else
        node.appendChild(doc.createTextNode('1'));
    end
    size_n.appendChild(node); 
    anno.appendChild(size_n);
    
    for m = 1:numel(f)
        color = cm.(f{m});
        if m <= 3
            Bin = I(:,:) >= color;
        else
            Bin = I(:,:) == color;
        end
        [y, x] = find(Bin);
        
        if numel(x) + numel(y) >= limit
            box = [ ...
                min(x-1), ...
                min(y-1), ...
                max(x-1), ...
                max(y-1) ...
                ];
            
            if box(3) - box(1) < min_ext(1) * 2
                center = (box(3) + box(1)) / 2;
                box(1) = max(0, center - min_ext(1));
                box(3) = min(Isz(2) - 1, center + min_ext(1));
            end
            
            if box(4) - box(2) < min_ext(2) * 2
                center = (box(4) + box(2)) / 2;
                box(2) = max(0, center - min_ext(2));
                box(4) = min(Isz(1) - 1, center + min_ext(2));
            end
            
            if m ~= 4
                object = createObjNode(doc, m, f{m}, box);
                anno.appendChild(object);
            end
            if m > 4
               object = createObjNode(doc, 4, 'r_fingertip', box);
               anno.appendChild(object);
            end
        end
    end
    
    outpath = strcat(outdir, '/', outfile);
    xmlwrite(outpath, doc);
end
