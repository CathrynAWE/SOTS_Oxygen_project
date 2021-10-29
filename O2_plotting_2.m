% This script plots Oxygen sensor data per deployment year for QC purposes

%clear all
%close all

mooring{1} = 'SOFS-9-2020';
mooring{2} = 'SOFS-8-2019';
mooring{3} = 'SOFS-7.5-2018';
mooring{4} = 'SOFS-6-2017';
mooring{5} = 'FluxPulse-1-2016';
mooring{6} = 'SOFS-5-2015';
mooring{7} = 'SOFS-4-2013';
mooring{8} = 'SOFS-3-2012';
mooring{9} = 'SOFS-2-2011';
mooring{10} = 'SOFS-1-2010';
mooring{11} = 'Pulse-11-2015';
mooring{12} = 'Pulse-10-2013';
mooring{13} = 'Pulse-9-2012';
mooring{14} = 'Pulse-8-2011';
mooring{15} = 'Pulse-7-2010';
mooring{16} = 'Pulse-6-2009';

% 
% for i = 1:size(mooring,2)
%     plot_O2(mooring{i});
% end

for i = 1:1
   plot_O2(mooring{i});
end


function plot_O2(mooring)
% display which mooring you are working on
    disp(mooring)

    path = 'C:\Users\cawynn\cloudstor\Shared\sots-Oxygen';
% construct the file names and paths
% Optode file first, either raw or with added attributes    
    Optode_filename = dir([path '\' mooring '\optode\netCDF\IMOS*.nc']);
    if isempty(Optode_filename)
        Optode_filename = dir([path '\' mooring '\optode\netCDF\*processed.nc']);
    end
    
    Optode_fn = [Optode_filename.folder '\' Optode_filename.name];
    
% next the SBE-ODO files    
    SBE37ODO_filenames = dir([path '\' mooring '\SBE37-ODO\*.nc']);
    for i = 1:size(SBE37ODO_filenames,1)
        SBE37ODO_fn{i} = [SBE37ODO_filenames(i).folder '\' SBE37ODO_filenames(i).name];
    end
    

% next any additional O2 sensors there might have been    
    add_sensor_filenames = dir([path '\' mooring '\additional_O2_sensors\*.nc']);
    for i = 1:size(add_sensor_filenames,1)
        add_sensor_fn{i} = [add_sensor_filenames(i).folder '\' add_sensor_filenames(i).name];
    end

   
% compile all the files to plot
    if (size(SBE37ODO_filenames,1) ~=0)
        files_to_plot = SBE37ODO_fn;
        l=length(files_to_plot);
        files_to_plot{l+1} = Optode_fn;
     
    else
        files_to_plot = Optode_fn;
   
    end

    
    if ~isempty(add_sensor_filenames)
        if ischar(files_to_plot)
            files_to_plot = mat2cell(files_to_plot,1);
        end
                  
        l = length(files_to_plot);
        for i = 1:length(add_sensor_fn)
            files_to_plot{l+i} = add_sensor_fn{i};
           
        end
    end

        
% create a figure to add all the data to
    fig = figure();
    cl = get(groot,'defaultAxesColorOrder');
    pn = 1;
    if ischar(files_to_plot)
        file = files_to_plot
        k=1;
        
    % define the variable you want to plot
        plotVar = 'DOX2';
    % read the variable and its unit from the netCDF file
        var = ncread(file,plotVar);
        var_unit = ncreadatt(file, plotVar, 'units');
        time = ncread(file, 'TIME') + datetime(1950,1,1);
    % deal with the fact that the nominal depth variable wasn't always called
    % that
        try 
            nominal_depth = ncread(file, 'NOMINAL_DEPTH');
        catch ME
            if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:unknownLocation'))
                try
                    nominal_depth = ncread(file, 'DEPTH_DOX2');
                catch ME
                    if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:unknownLocation'))
                        try
                            nominal_depth = ncreadatt(file, plotVar, 'sensor_depth')
                            catch ME
                                if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'))
                                    nominal_depth = 0;
                                end
                        end
                    end
                end
            end
        end
                        
                        
               
    % fetch the instrument name and serial number for the figure legend
        try
            instrument = ncreadatt(file, '/', 'instrument');
            sn = ncreadatt(file, '/', 'instrument_serial_number');
        catch ME
            if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'));
                try
                    instrument = ncreadatt(file, plotVar, 'sensor_name');
                    sn = ncreadatt(file, plotVar, 'sensor_serial_number');
                catch ME
                    if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'));
                        instrument = 'unknown';
                        sn = 'unknown';
                    end
                end
            end
        end
      

        legend_name = [num2str(nominal_depth) 'm; ' instrument ' ' sn];

        %if nominal_depth <850
            p(pn) = plot(time,var,'DisplayName',legend_name, 'Color', cl(k,:));
            hold on
            pn = pn + 1;
        %end
        
    else
    
        for k = 1:length(files_to_plot)
            file = files_to_plot{k}
    
    % define the variable you want to plot
            plotVar = 'DOX2';
    % read the variable and its unit from the netCDF file
            try
                var = ncread(file,plotVar);
                var_unit = ncreadatt(file, plotVar, 'units');
                %var_name = ncreadatt(file, plotVar, 'long_name');
                %varQCname = strsplit(ncreadatt(file, plotVar, 'ancillary_variables'), ' ');
                %varQC = ncread(file, varQCname{2});
                time = ncread(file, 'TIME') + datetime(1950,1,1);
            catch ME
                if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:unknownLocation'))
                    disp('netCDF variable not found')
                    var=[];
                end
            end
    % deal with the fact that the nominal depth variable wasn't always called
    % that
            try 
                nominal_depth = ncread(file, 'NOMINAL_DEPTH');
            catch ME
                if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:unknownLocation'))
                    try
                        nominal_depth = ncread(file, 'DEPTH_DOX2');
                    catch ME
                        if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:unknownLocation'))
                            try
                                nominal_depth = ncreadatt(file, plotVar, 'sensor_depth');
                                catch ME
                                    if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'))
                                        nominal_depth = 0;
                                    end
                            end
                        end
                    end
                end
            end


            % fetch the instrument name and serial number for the figure legend
            try
                instrument = ncreadatt(file, '/', 'instrument');
                sn = ncreadatt(file, '/', 'instrument_serial_number');
            catch ME
                if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'));
                    try
                        instrument = ncreadatt(file, plotVar, 'sensor_name');
                        sn = ncreadatt(file, plotVar, 'sensor_serial_number');
                    catch ME
                        if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'));
                            instrument = 'unknown';
                            sn = 'unknown';
                        end
                    end
                end
            end
            
            
%             if nominal_depth <850
            if isempty(var)
                disp('netCDF variable not found')
            elseif size(var,2)==1

                legend_name = [num2str(nominal_depth) 'm; ' instrument ' ' sn];
                p(pn) = plot(time,var,'DisplayName',legend_name, 'Color', cl(k,:));
                hold on
                pn = pn + 1;
            else
                for n = 1:size(var,1)
                    if strcmp(instrument,'unknown')
                        instrument = 'unknown';
                    else
                        ins = split(instrument,';');
                    end
                    if strcmp(sn,'unknown')
                        sn = 'unknown';
                    else
                        snspl = split(sn,';');
                    end
                    depth = split(nominal_depth,';');

                    legend_name = [num2str(depth{n}) 'm; ' ins{n} ' ' snspl{n}];
                    p(pn) = plot(time,var(n,:),'DisplayName',legend_name, 'Color', cl(k,:));
                    hold on
                    pn = pn + 1;
                end
            end
        end
    end
   

    try
        timestart = datetime(ncreadatt(Optode_fn, '/', 'time_deployment_start'), 'InputFormat', 'yyyy-MM-dd''T''HH:mm:ss''Z''');
        timeend = datetime(ncreadatt(Optode_fn, '/', 'time_deployment_end'), 'InputFormat', 'yyyy-MM-dd''T''HH:mm:ss''Z''');

    catch ME
        if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'));
            timestart = time(1);
            timeend = time(length(time));
        end
    end


    grid on
    ylabel([plotVar ' (' var_unit ')'], 'Interpreter', 'none')
    t = title({mooring},'Interpreter','tex');
    %h= legend(p,'Orientation','horizontal','Location', 'southoutside');
    h= legend(p,'Orientation','vertical','Location', 'southoutside');
    h.FontSize = 10;
    set(h, 'FontSize', 10)
    xlim([timestart timeend]);
    hold off
    
end


