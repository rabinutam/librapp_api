class DisableCSRF(object):
    def process_request(self, request):
        '''
        alt: request._dont_enforce_csrf_checks = True
        '''
        # Avoid checking the request, just say its done
        request.csrf_processing_done = True
