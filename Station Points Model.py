"""
Model exported as python.
Name : station points
Group : 
With QGIS : 31612
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsCoordinateReferenceSystem
import processing


class StationPoints(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('Qchainagepts', 'Q chainage pts', defaultValue=None, types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterString('RoadName', 'Road Name', multiLine=False, defaultValue='ROAD'))
        self.addParameter(QgsProcessingParameterFeatureSink('_p50_wgs84', '_P50_WGS84', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('_p10_wgs84', '_P10_WGS84', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(7, model_feedback)
        results = {}
        outputs = {}

        # Refactor fields (50)
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '$id-1','length': 10,'name': 'fid','precision': 0,'type': 4},{'expression': '\"cngfeet\"','length': 23,'name': 'cngfeet','precision': 15,'type': 6},{'expression': 'concat(($id-1),\'+0\')','length': 254,'name': 'Station','precision': 0,'type': 10},{'expression': ' @RoadName','length': 254,'name': 'Road_Name','precision': 0,'type': 10},{'expression': '\"cngfeet\" % 50','length': 254,'name': 'Filter_50','precision': 0,'type': 10}],
            'INPUT': parameters['Qchainagepts'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RefactorFields50'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Refactor fields
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '$id-1','length': 10,'name': 'fid','precision': 0,'type': 4},{'expression': '\"cngfeet\"','length': 23,'name': 'cngfeet','precision': 15,'type': 6},{'expression': 'concat(($id-1),\'+0\')','length': 254,'name': 'Station','precision': 0,'type': 10},{'expression': ' @RoadName','length': 254,'name': 'Road_Name','precision': 0,'type': 10}],
            'INPUT': parameters['Qchainagepts'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RefactorFields'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': '\"cngfeet\" % 50 = 0',
            'INPUT': outputs['RefactorFields50']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Reproject layer
        alg_params = {
            'INPUT': outputs['RefactorFields']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': parameters['_p10_wgs84']
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['_p10_wgs84'] = outputs['ReprojectLayer']['OUTPUT']

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['ReprojectLayer']['OUTPUT'],
            'STYLE': 'C:\\TBN\\As Builts QGIS Project\\2023-02-03_1600---QGIS_VETRO_TEMP\\LINES+POINTS\\TEMP_PTS.qml'
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Reproject layer(50)
        alg_params = {
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': parameters['_p50_wgs84']
        }
        outputs['ReprojectLayer50'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['_p50_wgs84'] = outputs['ReprojectLayer50']['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['ReprojectLayer50']['OUTPUT'],
            'STYLE': 'C:\\TBN\\As Builts QGIS Project\\2023-02-03_1600---QGIS_VETRO_TEMP\\LINES+POINTS\\TEMP_PTS.qml'
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'station points'

    def displayName(self):
        return 'station points'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return StationPoints()
