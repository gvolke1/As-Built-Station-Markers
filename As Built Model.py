"""
Model exported as python.
Name : As Built Points
Group : 
With QGIS : 31612
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class AsBuiltPoints(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('LateraltoSnapTo', 'Lateral to Snap To', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('StationPoints50ft', 'Station Points 50ft', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('_as_built', '_As_Built', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 1,
            'INPUT': parameters['StationPoints50ft'],
            'REFERENCE_LAYER': parameters['LateraltoSnapTo'],
            'TOLERANCE': 10,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Refactor fields
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '\"fid\"','length': 0,'name': 'fid','precision': 0,'type': 4},{'expression': '\"id\"','length': 254,'name': 'id','precision': 0,'type': 10},{'expression': '\"Name\"','length': 254,'name': 'Name','precision': 0,'type': 10},{'expression': 'case\r\n\twhen \"fid\"=5 then \'00+50\'\r\n\twhen \"fid\"<=95 THEN concat(\'0\'||(left(\"fid\",1)||(\'+\')||right(\"fid\",1))||\'0\')\r\n\twhen (\"fid\")>95 THEN concat(left(\"fid\",2))||\'+\'||right(\"fid\",1)||\'0\'\r\nend','length': 254,'name': 'Station','precision': 0,'type': 10},{'expression': '\"DoC_Inches\"','length': 0,'name': 'DoC_Inches','precision': 0,'type': 6},{'expression': '\"EoP_Feet\"','length': 0,'name': 'EoP_Feet','precision': 0,'type': 6}],
            'INPUT': outputs['SnapGeometriesToLayer']['OUTPUT'],
            'OUTPUT': parameters['_as_built']
        }
        outputs['RefactorFields'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['_as_built'] = outputs['RefactorFields']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['RefactorFields']['OUTPUT'],
            'STYLE': 'C:\\TBN\\As Builts QGIS Project\\2023-02-03_1600---QGIS_VETRO_TEMP\\LINES+POINTS\\TEMP_AB.qml'
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'As Built Points'

    def displayName(self):
        return 'As Built Points'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return AsBuiltPoints()
