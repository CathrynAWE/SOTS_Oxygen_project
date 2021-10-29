% This script plots Oxygen sensor data per deployment year 
% for QC purposes the figure is divided in subplots,
% pressure (so the colour coding is obivous for the other plots)
% DOXS, DOX2, TEMP and PSAL (the latter two from the same sensor as O2)

clear
close all

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


for i = 1:1
   plotVar={'PRES';'DOX2';'DOXS';'TEMP';'PSAL'};
   plot_O2(mooring{i},plotVar);
   
end


function [var, var_unit, varQC, time, timestart, timeend, pres, nominal_depth, instrument, sn] = read_variables(Optode_fn, file, plotVar)
    % read the variable and its unit from the netCDF file
    % time, converted to datetime
    time = ncread(file, 'TIME') + datetime(1950,1,1);
    % the variable and its units        
    try
        var = ncread(file,plotVar);
        var_unit = ncreadatt(file, plotVar, 'units');

    catch ME
        if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:unknownLocation'))
            disp('netCDF variable not found')
            var=[];
            var_unit=[];
        end
    end
% the variable QC flags
    if ~isempty(var)
        try 
            varQCname = strsplit(ncreadatt(file, plotVar, 'ancillary_variables'), ' ');
            varQC = ncread(file, varQCname{1});
        catch ME
            if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'))
                varQC = [];
            end
        end
    else
        varQC=[];
    end
% if plotVar is DOXS (oxygen saturation) then either find it or calculate
% it
    if plotVar == 'DOXS' & isempty(var)
        try
            oxsol = ncread(file,'OXSOL');
            dox2 = ncread(file, 'DOX2');
            var = dox2./oxsol;
        catch ME
            if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'));
                var=[];
            end
        end
    end
% the in and out of water times, or else just the start and end times       
     try
        timestart = datetime(ncreadatt(Optode_fn, '/', 'time_deployment_start'), 'InputFormat', 'yyyy-MM-dd''T''HH:mm:ss''Z''');
        timeend = datetime(ncreadatt(Optode_fn, '/', 'time_deployment_end'), 'InputFormat', 'yyyy-MM-dd''T''HH:mm:ss''Z''');

        catch ME
            if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:libraryFailure'));
                timestart = time(1);
                timeend = time(length(time));
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
                            elseif (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:unknownLocation'))
                                nominal_depth = 0;
                            end
                    end
                end
            end
        end
    end
% pressure or alternatively nominal depth          
    try
        pres = ncread(file,'PRES');
    catch ME
        if (strcmp(ME.identifier,'MATLAB:imagesci:netcdf:unknownLocation'))
            pres = nominal_depth * ones(size(time));
            
        end
    end
    
    if ischar(nominal_depth)
        nominal_depth = str2num(nominal_depth);
    end
    
    if plotVar == 'PRES'
        var = pres;
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
end


function plot_O2(mooring,plotVar)
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
    fig=figure()
    hold on
    
    if ischar(files_to_plot)
        file = files_to_plot
        k=1;
        for v =1:length(plotVar)
            disp(plotVar{v})
            [var, var_unit, varQC, time, timestart, timeend, pres, nominal_depth, instrument, sn] = read_variables(Optode_fn, file, plotVar{v});

            legend_name = [num2str(nominal_depth) 'm; ' instrument ' ' sn];

            subplot(length(plotVar),1,v)
            hold on
            grid on

            if isempty(var)
                disp('netCDF variable not found')
            elseif size(var,2)==1
                % take QC flags into account if they exist
                if ~isempty(varQC)
                    varmsk = var;
                    varmsk(varQC>2)=NaN;
                else
                    varmsk = var;
                    disp('no QC flags found')
                end   
                legend_name = [num2str(nominal_depth) 'm; ' instrument ' ' sn];
                p = plot(time,varmsk,'DisplayName',legend_name);
                xlim([timestart timeend]);
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
                    if ~isempty(varQC)
                        varmsk = var;
                        for n = 1:size(var,1)
                            varmsk(n,varQC(n,:)>2)=NaN;
                        end
                    else
                        varmsk = var;
                    end 
                    p= plot(time,varmsk(n,:),'DisplayName',legend_name);
                    xlim([timestart timeend]);
                end
            end
            %ylabel([plotVar{v} ' (' var_unit ')'], 'Interpreter', 'none')

            ylabel(plotVar{v}, 'Interpreter', 'none')
            if plotVar{v} == 'PRES'
                set(gca, 'YDir','reverse')
            end
            hold off
        end
        %h= legend('Orientation','vertical','Location', 'southoutside');
        %h.FontSize = 6;
        %set(h, 'FontSize', 6)
        subplot(length(plotVar),1,1)
        t = title({mooring},'Interpreter','tex');
        %h= legend(p,'Orientation','horizontal','Location', 'southoutside');

    else
        for k = 1:length(files_to_plot)
            file = files_to_plot{k}
            k

            for v = 1:length(plotVar)
                disp(plotVar{v})
                [var, var_unit, varQC, time, timestart, timeend, pres, nominal_depth, instrument, sn] = read_variables(Optode_fn, file, plotVar{v});

                legend_name = [num2str(nominal_depth) 'm; ' instrument ' ' sn];

                subplot(length(plotVar),1,v)
                hold on
                grid on

                if isempty(var)
                    disp('netCDF variable not found for plotting')
                elseif size(var,2)==1
                    % take QC flags into account if they exist
                    if ~isempty(varQC)
                        varmsk = var;
                        varmsk(varQC>2)=NaN;
                    else
                        varmsk = var;
                        disp('no QC flags found')
                    end   
                    legend_name = [num2str(nominal_depth) 'm; ' instrument ' ' sn];
                    p = plot(time,varmsk,'DisplayName',legend_name);
                    xlim([timestart timeend]);
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
                        if ~isempty(varQC)
                            varmsk = var;
                            for n = 1:size(var,1)
                                varmsk(n,varQC(n,:)>2)=NaN;
                            end
                        else
                            varmsk = var;
                        end 
                        p= plot(time,varmsk(n,:),'DisplayName',legend_name);
                        xlim([timestart timeend]);
                    end
                end
                %ylabel([plotVar{v} ' (' var_unit ')'], 'Interpreter', 'none')

                ylabel(plotVar{v}, 'Interpreter', 'none')
                if plotVar{v} == 'PRES'
                    set(gca, 'YDir','reverse')
                end
                hold off
                
                
            end
            %h= legend('Orientation','vertical','Location', 'southoutside');
            %h.FontSize = 6;
            %set(h, 'FontSize', 6)

            subplot(length(plotVar),1,1)
            t = title({mooring},'Interpreter','tex');
            %h= legend(p,'Orientation','horizontal','Location', 'southoutside');

        end
    end
    name = [mooring , '_subplots_for_QC']; 
    %print(fig,name, '-dpng')
end
