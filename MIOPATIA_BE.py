import pandas as pd
import numpy as np
from MIOPATIA_db import DB_management as DB
from PyQt5 import QtCore, QtWidgets, uic, QtGui


class BACK_END(object):
    """ Code associatted to controls, buttons, text boxes etc.
    """
    def __init__(self,parent_wdg,shared_data,visa,dataview):
        self.sd = shared_data
        self.pw = parent_wdg
        self.vi = visa
        self.dv = dataview
        self.flag = True

     # Controlled casting to avoid data intro errors. Read text or button_ID
    def value_control(self,objeto,limits=[0,1E12],type='int',qt_obj="QLineEdit"):
        try:
            if qt_obj == "QLineEdit":
                aux = eval(type)(objeto.text())
            elif qt_obj == "QButtonGroup":
                aux = eval(type)(objeto.checkedId())
            elif qt_obj == "QCheckBox":
                aux = eval(type)(objeto.isChecked())

            if ((aux >= limits[0]) and (aux <= limits[1])):
                return eval(type)(aux)
            else:
                if (aux > limits[1]):
                    objeto.setText(str(limits[1]))
                    return eval(type)(limits[1])
                else:
                    if (aux < limits[0]):
                        objeto.setText(str(limits[0]))
                        return eval(type)(limits[0])
        except ValueError:
            self.dv.append_plus("ERROR EN VALOR")
            objeto.setText(str(limits[0]))
            return limits[0]

    def save_config(self):
        self.sd.config_write()

    def redraw_measure(self):
        # self.dv.append_plus("CONTINUAR")
        if (len(self.sd.freq))>0:
            self.dv.show_measurement(self.pw.comboBox_trazaA.currentIndex(),
                                     self.pw.comboBox_trazaB.currentIndex())
        else:
            self.dv.append_plus("NO HAY DATOS QUE MOSTRAR")
        self.pw.canvas1.draw()

    def medir(self):
        self.pw.MEDIR.setEnabled(False)
        #app.processEvents()
        #self.dv.append_plus("MEDIR")
        # self.vi.config_measurement()
        self.vi.measure()
        self.dv.show_measurement(self.pw.comboBox_trazaA.currentIndex(),
                                 self.pw.comboBox_trazaB.currentIndex())
        self.pw.canvas1.draw()
        self.pw.MEDIR.setEnabled(True)

    def load_m(self):
        self.dv.append_plus("CARGA MEDIDA")
        file = self.sd.def_cfg['load_mfile_name']
        try:
            data = pd.read_csv(file,header=0,
                            names=['Freq','Z_mod','Z_Fase', 'Err',
                                    'Eri','E_mod','E_fase','R','X'],
                            delim_whitespace=True)
        except:
            self.dv.append_plus("Fichero no encontrado\n")
        else:
            self.dv.append_plus(file)
            self.dv.show_data(self.pw.comboBox_trazaA.currentIndex(),
                              self.pw.comboBox_trazaB.currentIndex(),
                              data)
            self.pw.canvas2.draw()

    def load_m_fit(self):
        self.dv.append_plus("CARGA MEDIDA")
        file = self.sd.def_cfg['load_mfile_fit']
        try:
            data = pd.read_csv(file,header=0,
                            names=['Freq','Z_mod','Z_Fase', 'Err',
                                    'Eri','E_mod','E_fase','R','X'],
                            delim_whitespace=True)
        except:
            self.dv.append_plus("Fichero no encontrado\n")
        else:
            self.dv.append_plus(file)
            self.dv.show_data_fit(self.pw.comboBox_mag_fit.currentIndex(),
                                  self.pw.comboBox_fit_alg.currentText(),
                                  data)
            self.pw.canvas3.draw()

    def load_h5_fit(self):
        self.dv.append_plus("CARGA MEDIDA BASE DATOS H5")
        file = self.sd.def_cfg['load_h5file_name']
        try:
            hdf_db = DB(file,self.dv)
            #hdf_db = pd.HDFStore(file,'r',complib="zlib",complevel=4)
            #pollos = hdf_db.get('data/index/pollos')
            #indice_medidas = hdf_db.get('data/index/medidas')
            #tabla = hdf_db.get('data/tabla')
            #columns=['Freq','Z_mod','Z_Fase','Err','Eri','E_mod','E_fase','R','X']
        except:
            self.dv.append_plus("Fichero no encontrado\n")
        else:
            self.dv.append_plus(file)
            pollo_sel = int(self.pw.spinBox_pollo.value())
            medida_sel = int(self.pw.spinBox_medida.value())
            #inicio_medida = indice_medidas['primero'][int(pollo_sel[self.pw.spinBox_medida.value()])]
            #fin_medida    = indice_medidas['ultimo'][int(pollo_sel[self.pw.spinBox_medida.value()])]
            #data = tabla[inicio_medida:fin_medida]
            #data = tabla[(tabla['Pollo']==pollo_sel)&(tabla['Medida']==medida_sel)]
            data = hdf_db.lee_medida_BD(pollo_sel,medida_sel)

            #

            self.sd.pollo_fitado = pollo_sel
            self.sd.medida_fitada = medida_sel

            if (data.empty):
                self.dv.append_fit("Medidas no encontradas en la Base de Datos")
            else:
                self.dv.show_data_fit(self.pw.comboBox_mag_fit.currentIndex(),
                                      self.pw.comboBox_fit_alg.currentText(),
                                      data)
                self.pw.canvas3.draw()

    def measure_fit(self):
        self.dv.append_plus("AJUSTE DE DATOS MEDIDOS")
        data_array = np.concatenate([np.reshape(self.sd.freq,(-1,1)),
                                     np.reshape(self.sd.Z_mod_data,(-1,1)),
                                     np.reshape(self.sd.Z_fase_data,(-1,1)),
                                     np.reshape(self.sd.Err_data,(-1,1)),
                                     np.reshape(self.sd.Eri_data,(-1,1)),
                                     np.reshape(self.sd.Er_mod_data,(-1,1)),
                                     np.reshape(self.sd.Er_fase_data,(-1,1)),
                                     np.reshape(self.sd.R_data,(-1,1)),
                                     np.reshape(self.sd.X_data,(-1,1))],
                                     axis=1)
        data_frame = pd.DataFrame(data_array,
                                  columns=['Freq','Z_mod','Z_Fase','Err','Eri',
                                           'E_mod','E_fase','R','X'])
        self.dv.show_data_fit(self.pw.comboBox_mag_fit.currentIndex(),
                              self.pw.comboBox_fit_alg.currentText(),
                              data_frame,
                              self.pw.spinBox_pollo_db.value(),
                              self.pw.spinBox_medida_db.value())
        self.pw.canvas3.draw()

    def save_fit(self):
        self.dv.append_plus("SALVA FIT BASE DATOS H5")
        file = self.sd.def_cfg['load_h5file_name']
        #try:
        hdf_db = pd.HDFStore(file,'a',complib="zlib",complevel=4)
        #fit_data = hdf_db.get('data/fit')
        print(self.sd.pollo_fitado,self.sd.medida_fitada)
        #fit_data.loc[self.sd.pollo_fitado]=self.sd.fit_data_frame.to_numpy()
        hdf_db.append('data/fit',self.sd.fit_data_frame)
        hdf_db.close()
        #except:
        #    self.dv.append_plus("Error en Base de Datos\n")
        #else:


    def save_m(self):
        def justify(input_str,n_char):
            string = input_str+''.join([' ']*(n_char-len(input_str)))
            return string.strip('"')

        self.dv.append_plus("SALVA MEDIDA")
        file_save = self.sd.def_cfg['save_mfile_name']
        try:
            data_array = np.concatenate([np.reshape(self.sd.freq,(-1,1)),
                                         np.reshape(self.sd.Z_mod_data,(-1,1)),
                                         np.reshape(self.sd.Z_fase_data,(-1,1)),
                                         np.reshape(self.sd.Err_data,(-1,1)),
                                         np.reshape(self.sd.Eri_data,(-1,1)),
                                         np.reshape(self.sd.Er_mod_data,(-1,1)),
                                         np.reshape(self.sd.Er_fase_data,(-1,1)),
                                         np.reshape(self.sd.R_data,(-1,1)),
                                         np.reshape(self.sd.X_data,(-1,1))],
                                         axis=1)
            data_frame = pd.DataFrame(data_array,
                                      columns=['Freq','Z_mod','Z_Fase','Err','Eri',
                                               'E_mod','E_fase','R','X'])
            data_frame.to_csv(file_save, sep=' ', index=False, float_format='%+13.6e',
                              # header=[justify('Freq',15).strip('"'), justify('Z_mod',15),
                              #         justify('Z_Fase',15), justify('Err',15),
                              #         justify('Eri',15), justify('E_mod',15),
                              #         justify('E_fase',15), justify('R',15),
                              #         justify('X',15)]
                              header=True)
        except:
            self.dv.append_plus("El fichero de datos no se ha podido salvar\n")
        else:
            self.dv.append_plus(file_save)


    def go_cal(self):
        self.dv.append_plus("CALIBRAR")
        self.vi.config_calibration()
        if (self.sd.def_cfg['conf_cal']['value'] == 0):
            # Calibración CARGA - ABIERTO - CORTO
            self.vi.cal_load_open_short()

        elif (self.sd.def_cfg['conf_cal']['value'] == 1):
            # Calibración ABIERTO - CORTO
            self.vi.cal_open_short()

    def load_cal(self):
        self.dv.append_plus("CARGAR CALIBRACIÓN")
        file = self.sd.def_cfg['load_cal_file_name']
        try:
            data = pd.read_csv(file,header=0,
                            names=['Freq','OPEN_R','OPEN_X','SHORT_R','SHORT_X',
                                     'LOAD_R','LOAD_X'],
                            delim_whitespace=True)
        except:
            self.dv.append_plus("Fichero no encontrado\n")
        else:
            self.dv.append_plus(file)
            self.sd.COM_OPEN_data_R = data['OPEN_R']
            self.sd.COM_OPEN_data_X = data['OPEN_X']
            self.sd.COM_SHORT_data_R = data['SHORT_R']
            self.sd.COM_SHORT_data_X = data['SHORT_X']
            self.sd.COM_LOAD_data_R = data['LOAD_R']
            self.sd.COM_LOAD_data_X = data['LOAD_X']

            self.vi.send_calibration()


    def save_cal(self):
        self.dv.append_plus("SALVAR CALIBRACIÓN")
        self.vi.get_calibration()

        file_save = self.sd.def_cfg['save_cal_file_name']
        try:
            print(len(self.sd.COM_OPEN_data_R))

            data_array = np.concatenate([np.reshape(self.sd.freq,(-1,1)),
                                         np.reshape(self.sd.COM_OPEN_data_R,(-1,1)),
                                         np.reshape(self.sd.COM_OPEN_data_X,(-1,1)),
                                         np.reshape(self.sd.COM_SHORT_data_R,(-1,1)),
                                         np.reshape(self.sd.COM_SHORT_data_X,(-1,1)),
                                         np.reshape(self.sd.COM_LOAD_data_R,(-1,1)),
                                         np.reshape(self.sd.COM_LOAD_data_X,(-1,1))]
                                         ,axis=1)
            data_frame = pd.DataFrame(data_array,
                                      columns=['Freq','OPEN_R','OPEN_X','SHORT_R','SHORT_X',
                                               'LOAD_R','LOAD_X'])
            data_frame.to_csv(file_save, sep=' ', index=False, float_format='%+13.6e',header=True)
        except:
            self.dv.append_plus("El fichero de calibración no se ha podido salvar\n")
        else:
            self.dv.append_plus(file_save)


    def default_data(self):

        for i in self.pw.mirror.keys():
            for j in self.pw.mirror[i]['array']:
                if self.pw.mirror[i]['qt'] == 'QLineEdit':
                    eval("self.pw."+j).setText(str(self.sd.def_cfg[i]['value']))
                elif self.pw.mirror[i]['qt'] == 'QButtonGroup':
                    eval("self.pw."+j).button(self.sd.def_cfg[i]['value']).setChecked(True)
                elif self.pw.mirror[i]['qt'] == 'QCheckBox':
                    eval("self.pw."+j).setChecked(self.sd.def_cfg[i]['value'])

        for i in self.pw.paths.keys():
            aux = self.pw.paths[i]
            eval("self.pw." + aux).setText(str(self.sd.def_cfg[i]))

        for i in self.pw.others.keys():
            aux = self.pw.others[i]['array']
            if self.pw.others[i]['qt'] == 'QLineEdit':
                eval("self.pw." + aux).setText(str(self.sd.def_cfg[i]['value']))
            elif self.pw.others[i]['qt'] == 'QButtonGroup':
                eval("self.pw." + aux).button(self.sd.def_cfg[i]['value']).setChecked(True)
            elif self.pw.others[i]['qt'] == 'QCheckBox':
                eval("self.pw." + aux).setChecked(self.sd.def_cfg[i]['value'])

        for i in self.pw.fit_param.keys():
            if i[0:6] == 'lparam':
                pass
            elif i[0:5] == 'param':
                pos = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])==i)[0][0]
                eval("self.pw." + self.pw.fit_param[i]['array'] + "_L").setText(str(self.sd.def_cfg['param_fit']['limits'][pos][0]))
                eval("self.pw." + self.pw.fit_param[i]['array'] + "_H").setText(str(self.sd.def_cfg['param_fit']['limits'][pos][1]))
                eval("self.pw." + self.pw.fit_param[i]['array']).setText(str(self.sd.def_cfg['param_fit']['value'][pos]))
            else:
                pos = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])==i)[0][0]
                eval("self.pw." + self.pw.fit_param[i]['array']).setText(str(self.sd.def_cfg['param_fit']['value'][pos]))


        # Default fit magnitude ABS(EPSILON)
        self.pw.comboBox_mag_fit.setCurrentIndex(4)

        self.store_data()
        self.store_fit()

        file_name = self.sd.def_cfg['io_h5file_name']
        base_io = DB(file_name,self.dv)
        ultimo_pollo,ultima_medida = base_io.chequea_ultimos()
        self.sd.def_cfg['ultimo_pollo'] = int(ultimo_pollo)
        self.sd.def_cfg['ultima_medida'] = int(ultima_medida)
        self.pw.last_pollo.display(self.sd.def_cfg['ultimo_pollo'])
        self.pw.last_medida.display(self.sd.def_cfg['ultima_medida'])



    def store_fit(self):
        # Add fit parameters to params
        for i in self.pw.fit_param.keys():
            if i[0:6] == 'lparam':
                pass
            else:
                pos = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])==i)[0][0]
                aux = self.pw.fit_param[i]['array']
                new_data = self.value_control(eval("self.pw."+ aux ), self.sd.def_cfg['param_fit']['limits'][pos],
                                            type = self.sd.def_cfg['param_fit']['type'][pos],
                                            qt_obj = self.pw.fit_param[i]['qt'])
                self.sd.def_cfg['param_fit']['value'][pos] = new_data

        # Add boundary array to params
        for i in self.pw.fit_param.keys():
            if i[0:5] == 'param':
                pos = np.argwhere(np.array(self.sd.def_cfg['param_fit']['names'])==i)[0][0]
                aux = self.pw.fit_param[i]['array']
                new_data_L = self.value_control(eval("self.pw."+ aux +"_L" ), [-1E12,1E12],
                                              type = self.sd.def_cfg['param_fit']['type'][pos],
                                              qt_obj = self.pw.fit_param[i]['qt'])
                new_data_H = self.value_control(eval("self.pw."+ aux +"_H" ), [-1E12,1E12],
                                              type = self.sd.def_cfg['param_fit']['type'][pos],
                                              qt_obj = self.pw.fit_param[i]['qt'])
                self.sd.def_cfg['param_fit']['limits'][pos] = [new_data_L, new_data_H]



    def store_data(self):
        for i in self.pw.mirror.keys():
            for j in self.pw.mirror[i]['array']:
                new_data = self.value_control(eval("self.pw."+j), self.sd.def_cfg[i]['limits'],
                                              type = self.sd.def_cfg[i]['type'],
                                              qt_obj = self.pw.mirror[i]['qt'])
                def_data = self.sd.def_cfg[i]['value']
                if def_data != new_data:
                    self.sd.def_cfg[i]['value'] = new_data
                    break

        for i in self.pw.paths.keys():
            new_data = eval("self.pw."+self.pw.paths[i]).text()
            self.sd.def_cfg[i] = new_data

        for i in self.pw.others.keys():
            aux = self.pw.others[i]['array']
            new_data = self.value_control(eval("self.pw." + aux), self.sd.def_cfg[i]['limits'],
                                          type = self.sd.def_cfg[i]['type'],
                                          qt_obj = self.pw.others[i]['qt'])
            self.sd.def_cfg[i]['value'] = new_data

        # UPDATE
        for i in self.pw.mirror.keys():
            for j in self.pw.mirror[i]['array']:
                if self.pw.mirror[i]['qt'] == 'QLineEdit':
                    eval("self.pw."+j).setText(str(self.sd.def_cfg[i]['value']))
                elif self.pw.mirror[i]['qt'] == 'QButtonGroup':
                    eval("self.pw."+j).button(self.sd.def_cfg[i]['value']).setChecked(True)
                elif self.pw.mirror[i]['qt'] == 'QCheckBox':
                    eval("self.pw."+j).setChecked(self.sd.def_cfg[i]['value'])

    def save_measure_to_DB(self):
        file_name = self.sd.def_cfg['io_h5file_name']
        base_io = DB(file_name,self.dv)
        try:
            data_array = np.concatenate([np.reshape(self.sd.freq,(-1,1)),
                                         np.reshape(self.sd.Z_mod_data,(-1,1)),
                                         np.reshape(self.sd.Z_fase_data,(-1,1)),
                                         np.reshape(self.sd.Err_data,(-1,1)),
                                         np.reshape(self.sd.Eri_data,(-1,1)),
                                         np.reshape(self.sd.Er_mod_data,(-1,1)),
                                         np.reshape(self.sd.Er_fase_data,(-1,1)),
                                         np.reshape(self.sd.R_data,(-1,1)),
                                         np.reshape(self.sd.X_data,(-1,1))],
                                         axis=1)
            # data_frame = pd.DataFrame(data_array,
            #                           columns=['Freq','Z_mod','Z_Fase','Err','Eri',
            #                                    'E_mod','E_fase','R','X'])
        except:
            self.dv.append_plus("El fichero de datos no se ha podido salvar\n")
        else:
            last_pollo,last_medida = base_io.escribe_medida_BD(self.pw.spinBox_pollo_db.value(),
                                                                self.pw.spinBox_medida_db.value(),
                                                                data_array,
                                                                self.pw.spinBox_pollo_db_2.value())
            self.sd.def_cfg['ultimo_pollo'] = int(last_pollo)
            self.sd.def_cfg['ultima_medida'] = int(last_medida)
            self.pw.last_pollo.display(self.sd.def_cfg['ultimo_pollo'])
            self.pw.last_medida.display(self.sd.def_cfg['ultima_medida'])
            self.dv.append_plus("SALVA MEDIDA en BASE de DATOS")

class BROWSERS(object):
    """ File Browsers for config files, input and output files etc.
    """
    def __init__(self,parent_wdg,shared_data, dataview):
        self.sd = shared_data
        self.pw = parent_wdg
        self.dv = dataview

    def load_mfile_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Abrir fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_mfile_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path.setText(self.sd.def_cfg['load_mfile_name'])


    def save_mfile_browser(self):
        file_aux = QtWidgets.QFileDialog.getSaveFileName(self.pw,
                                        'Salvar fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['save_mfile_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.save_path.setText(self.sd.def_cfg['save_mfile_name'])


    def load_calibration_file_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Fichero de calibración',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de calibración (*.cal)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_cal_file_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path_2.setText(self.sd.def_cfg['load_cal_file_name'])


    def save_calibration_file_browser(self):
        file_aux = QtWidgets.QFileDialog.getSaveFileName(self.pw,
                                        'Fichero de calibración',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de calibración (*.cal)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['save_cal_file_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.save_path_2.setText(self.sd.def_cfg['save_cal_file_name'])

    def load_fit_data_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Abrir fichero de medidas',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de calibración (*.csv)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_mfile_fit'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path_3.setText(self.sd.def_cfg['load_mfile_fit'])

    def load_h5file_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Abrir fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.hdf)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['load_h5file_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path_4.setText(self.sd.def_cfg['load_h5file_name'])
        self.pw.spinBox_medida.setMaximum(12)
        self.pw.spinBox_pollo.setMaximum(100)

    def load_h5file_DB_browser(self):
        file_aux = QtWidgets.QFileDialog.getOpenFileName(self.pw,
                                        'Abrir fichero medida',
                                        self.sd.def_cfg['def_path'],
                                        "Ficheros de medida (*.hdf)")
        fname_aux = ([str(x) for x in file_aux])
        self.sd.def_cfg['io_h5file_name'] = fname_aux[0]
        #Trick for Qstring converting to standard string
        self.pw.load_path_db.setText(self.sd.def_cfg['io_h5file_name'])

        #self.dv.append_plus("CHEQUEA BASE DATOS H5")
        file_name = self.sd.def_cfg['io_h5file_name']
        base_io = DB(file_name,self.dv)
        ultimo_pollo,ultima_medida = base_io.chequea_ultimos()
        self.sd.def_cfg['ultimo_pollo'] = int(ultimo_pollo)
        self.sd.def_cfg['ultima_medida'] = int(ultima_medida)
        self.pw.last_pollo.display(self.sd.def_cfg['ultimo_pollo'])
        self.pw.last_medida.display(self.sd.def_cfg['ultima_medida'])
