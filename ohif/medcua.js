/** @type {AppTypes.Config} */
/**
 * MedCUA-Bench OHIF configuration.
 *
 * Uses the public OHIF demo DICOMweb endpoint containing the studies
 * referenced by the radiology and pathology task definitions.
 */
window.config = {
  routerBasename: '/',
  extensions: [],
  modes: [],
  showStudyList: true,
  showWarningMessageForCrossOrigin: false,
  strictZSpacingForVolumeViewport: true,
  showCPUFallbackMessage: true,
  showLoadingIndicator: true,
  maxNumberOfWebWorkers: 3,
  defaultDataSourceName: 'dicomweb',
  groupEnabledModesFirst: true,

  dataSources: [
    {
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'dicomweb',
      configuration: {
        friendlyName: 'MedCUA-Bench DICOM Server',
        name: 'MedCUA-Bench',
        wadoUriRoot: 'https://d14fa38qiwhyfd.cloudfront.net/dicomweb',
        qidoRoot: 'http://127.0.0.1:3002/dicomweb',
        wadoRoot: 'https://d14fa38qiwhyfd.cloudfront.net/dicomweb',
        qidoSupportsIncludeField: false,
        imageRendering: 'wadors',
        thumbnailRendering: 'wadors',
        enableStudyLazyLoad: true,
        supportsFuzzyMatching: false,
        supportsWildcard: true,
        staticWado: true,
        singlepart: 'bulkdata,video,pdf',
        bulkDataURI: {
          enabled: true,
          relativeResolution: 'studies',
        },
        omitQuotationForMultipartRequest: true,
      },
    },
  ],
};
