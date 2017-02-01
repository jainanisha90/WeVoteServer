# import_export_facebook/models.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from django.core.validators import RegexValidator
from django.db import models
from email_outbound.models import SEND_STATUS_CHOICES, TO_BE_PROCESSED
from wevote_functions.functions import generate_random_string, positive_value_exists
import facebook

FRIEND_INVITATION_FACEBOOK_TEMPLATE = 'FRIEND_INVITATION_FACEBOOK_TEMPLATE'
GENERIC_EMAIL_FACEBOOK_TEMPLATE = 'GENERIC_EMAIL_FACEBOOK_TEMPLATE'
KIND_OF_FACEBOOK_TEMPLATE_CHOICES = (
    (GENERIC_EMAIL_FACEBOOK_TEMPLATE,  'Generic Email'),
    (FRIEND_INVITATION_FACEBOOK_TEMPLATE, 'Invite Friend'),
)


class FacebookAuthResponse(models.Model):
    """
    This is the authResponse data from a Facebook authentication
    """
    voter_device_id = models.CharField(
        verbose_name="voter_device_id initiating Facebook Auth", max_length=255, null=False, blank=False, unique=True)
    datetime_of_authorization = models.DateTimeField(verbose_name='date and time of action', null=False, auto_now=True)

    # Comes from Facebook authResponse FACEBOOK_LOGGED_IN
    facebook_access_token = models.CharField(
        verbose_name="accessToken from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_expires_in = models.IntegerField(verbose_name="expiresIn from Facebook", null=True, blank=True)
    facebook_signed_request = models.TextField(verbose_name="signedRequest from Facebook", null=True, blank=True)
    facebook_user_id = models.BigIntegerField(verbose_name="facebook big integer id", null=True, blank=True)

    # Comes from FACEBOOK_RECEIVED_DATA
    facebook_email = models.EmailField(verbose_name='facebook email address', max_length=255, unique=False,
                                       null=True, blank=True)
    facebook_first_name = models.CharField(
        verbose_name="first_name from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_middle_name = models.CharField(
        verbose_name="first_name from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_last_name = models.CharField(
        verbose_name="first_name from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_profile_image_url_https = models.URLField(verbose_name='url of image from facebook', blank=True, null=True)

    def get_full_name(self):
        full_name = self.facebook_first_name if positive_value_exists(self.facebook_first_name) else ''
        full_name += " " if positive_value_exists(self.facebook_first_name) \
            and positive_value_exists(self.facebook_last_name) else ''
        full_name += self.facebook_last_name if positive_value_exists(self.facebook_last_name) else ''

        if not positive_value_exists(full_name) and positive_value_exists(self.facebook_email):
            full_name = self.email.split("@", 1)[0]

        return full_name


class FacebookLinkToVoter(models.Model):
    """
    This is the link between a Facebook account and a We Vote voter account
    """
    voter_we_vote_id = models.CharField(verbose_name="we vote id for the email owner", max_length=255, unique=True)
    facebook_user_id = models.BigIntegerField(verbose_name="facebook big integer id", null=False, unique=True)
    secret_key = models.CharField(
        verbose_name="secret key to verify ownership facebook account", max_length=255, null=False, unique=True)
    date_last_changed = models.DateTimeField(verbose_name='date last changed', null=False, auto_now=True)


class FacebookMessageOutboundDescription(models.Model):
    """
    A description of the Facebook direct message we want to send.
    """
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', message='Only alphanumeric characters are allowed.')

    kind_of_send_template = models.CharField(max_length=50, choices=KIND_OF_FACEBOOK_TEMPLATE_CHOICES,
                                             default=GENERIC_EMAIL_FACEBOOK_TEMPLATE)
    sender_voter_we_vote_id = models.CharField(
        verbose_name="we vote id for the sender", max_length=255, null=True, blank=True, unique=False)
    recipient_voter_we_vote_id = models.CharField(
        verbose_name="we vote id for the recipient if we have it", max_length=255, null=True, blank=True, unique=False)
    recipient_facebook_id = models.BigIntegerField(verbose_name="facebook big integer id", null=True, blank=True)
    recipient_facebook_email = models.EmailField(verbose_name='facebook email address', max_length=255, unique=False,
                                                 null=True, blank=True)
    recipient_fb_username = models.CharField(unique=True, max_length=20, validators=[alphanumeric], null=True)
    send_status = models.CharField(max_length=50, choices=SEND_STATUS_CHOICES, default=TO_BE_PROCESSED)


class FacebookUser(models.Model):
    """
    My facebook friends details, from the perspective of facebook id of me
    """
    facebook_user_id = models.BigIntegerField(verbose_name="facebook id of user", null=False, unique=False)
    facebook_user_name = models.CharField(
        verbose_name="User name from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_user_first_name = models.CharField(
        verbose_name="User's first_name from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_user_middle_name = models.CharField(
        verbose_name="User's middle_name from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_user_location_id = models.BigIntegerField(
        verbose_name="location id of Facebook user", null=True, unique=False)
    facebook_user_location_name = models.CharField(
        verbose_name="User's location name from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_user_gender = models.CharField(
        verbose_name="User's gender from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_user_birthday = models.CharField(
        verbose_name="User's birthday from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_user_last_name = models.CharField(
        verbose_name="User's last_name from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_user_cover_source = models.URLField(verbose_name='url of cover image from facebook', blank=True, null=True)
    facebook_user_about = models.CharField(
        verbose_name="User's About from Facebook", max_length=255, null=True, blank=True, unique=False)
    facebook_user_is_verified = models.BooleanField(
        verbose_name="User is verfired from Facebook", default=False)
    facebook_user_friend_total_count = models.BigIntegerField(
        verbose_name="total count of friends from facebook", null=True, unique=False)


class FacebookFriendsOfMe(models.Model):
    """
    My facebook friends ids, from the perspective of facebook id of me
    """
    facebook_id_of_me = models.BigIntegerField(verbose_name="facebook id of viewer", null=False, unique=False)
    facebook_id_of_my_friend = models.BigIntegerField(verbose_name="facebook id of my friend", null=False, unique=False)


class FacebookManager(models.Model):
    def __unicode__(self):
        return "FacebookManager"

    def create_facebook_link_to_voter(self, facebook_user_id, voter_we_vote_id):

        # Any attempts to save a facebook_link using either facebook_user_id or voter_we_vote_id that already
        #  exist in the table will fail, since those fields are required to be unique.
        facebook_secret_key = generate_random_string(12)

        try:
            facebook_link_to_voter = FacebookLinkToVoter.objects.create(
                facebook_user_id=facebook_user_id,
                voter_we_vote_id=voter_we_vote_id,
                secret_key=facebook_secret_key,
            )
            facebook_link_to_voter_saved = True
            success = True
            status = "FACEBOOK_LINK_TO_VOTER_CREATED"
        except Exception as e:
            facebook_link_to_voter_saved = False
            facebook_link_to_voter = FacebookLinkToVoter()
            success = False
            status = "FACEBOOK_LINK_TO_VOTER_NOT_CREATED"

        results = {
            'success':                      success,
            'status':                       status,
            'facebook_link_to_voter_saved': facebook_link_to_voter_saved,
            'facebook_link_to_voter':       facebook_link_to_voter,
        }
        return results

    def update_or_create_facebook_auth_response(
            self, voter_device_id, facebook_access_token, facebook_user_id, facebook_expires_in,
            facebook_signed_request,
            facebook_email, facebook_first_name, facebook_middle_name, facebook_last_name,
            facebook_profile_image_url_https):

        defaults = {
            "voter_device_id": voter_device_id,
        }
        if positive_value_exists(facebook_access_token):
            defaults["facebook_access_token"] = facebook_access_token
        if positive_value_exists(facebook_user_id):
            defaults["facebook_user_id"] = facebook_user_id
        if positive_value_exists(facebook_expires_in):
            defaults["facebook_expires_in"] = facebook_expires_in
        if positive_value_exists(facebook_signed_request):
            defaults["facebook_signed_request"] = facebook_signed_request
        if positive_value_exists(facebook_email):
            defaults["facebook_email"] = facebook_email
        if positive_value_exists(facebook_first_name):
            defaults["facebook_first_name"] = facebook_first_name
        if positive_value_exists(facebook_middle_name):
            defaults["facebook_middle_name"] = facebook_middle_name
        if positive_value_exists(facebook_last_name):
            defaults["facebook_last_name"] = facebook_last_name
        if positive_value_exists(facebook_profile_image_url_https):
            defaults["facebook_profile_image_url_https"] = facebook_profile_image_url_https

        try:
            facebook_auth_response, created = FacebookAuthResponse.objects.update_or_create(
                voter_device_id__iexact=voter_device_id,
                defaults=defaults,
            )
            facebook_auth_response_saved = True
            success = True
            status = "FACEBOOK_AUTH_RESPONSE_UPDATED_OR_CREATED"
        except Exception as e:
            facebook_auth_response_saved = False
            facebook_auth_response = FacebookAuthResponse()
            success = False
            created = False
            status = "FACEBOOK_AUTH_RESPONSE_NOT_UPDATED_OR_CREATED"

        results = {
            'success': success,
            'status': status,
            'facebook_auth_response_saved': facebook_auth_response_saved,
            'facebook_auth_response_created': created,
            'facebook_auth_response': facebook_auth_response,
        }
        return results

    def create_or_update_facebook_friends_of_me(self, facebook_id_of_me, facebook_id_of_my_friend):
        """
        We use this subroutine to create or update FacebookFriendsOfMe table with my friends facebook id.
        :param facebook_id_of_me:
        :param facebook_ids_of_my_friend:
        :return:
        """
        facebook_friends_of_me = FacebookFriendsOfMe()
        try:
            facebook_friends_of_me, created = FacebookFriendsOfMe.objects.update_or_create(
                facebook_id_of_me=facebook_id_of_me,
                facebook_id_of_my_friend=facebook_id_of_my_friend,
                defaults={
                    'facebook_id_of_me':        facebook_id_of_me,
                    'facebook_id_of_my_friend': facebook_id_of_my_friend
                }
            )
            facebook_friends_of_me_saved = True
            success = True
            status = "FACEBOOK_FRIENDS_OF_ME_CREATED"
        except Exception:
            facebook_friends_of_me_saved = False
            facebook_friends_of_me = FacebookFriendsOfMe()
            success = False
            status = "FACEBOOK_FRIENDS_OF_ME_NOT_CREATED"
        results = {
            'success':                      success,
            'status':                       status,
            'facebook_friends_of_me_saved': facebook_friends_of_me_saved,
            'facebook_friends_of_me':       facebook_friends_of_me,
            }
        return results

    def create_or_update_facebook_user(self, facebook_user_entry):
        """
        We use this subroutine to create or update FacebookUser table with my friends details.
        :param facebook_users:
        :return:
        """
        facebook_user = FacebookUser()
        try:
            # for facebook_user_entry in facebook_users:
            facebook_user, created = FacebookUser.objects.update_or_create(
                facebook_user_id=facebook_user_entry['facebook_user_id'],
                defaults={
                    'facebook_user_id':                 facebook_user_entry['facebook_user_id'],
                    'facebook_user_name':               facebook_user_entry['facebook_user_name'],
                    'facebook_user_first_name':         facebook_user_entry['facebook_user_first_name'],
                    'facebook_user_middle_name':        facebook_user_entry['facebook_user_middle_name'],
                    'facebook_user_last_name':          facebook_user_entry['facebook_user_last_name'],
                    'facebook_user_location_id':        facebook_user_entry['facebook_user_location_id'],
                    'facebook_user_location_name':      facebook_user_entry['facebook_user_location_name'],
                    'facebook_user_gender':             facebook_user_entry['facebook_user_gender'],
                    'facebook_user_birthday':           facebook_user_entry['facebook_user_birthday'],
                    'facebook_user_cover_source':       facebook_user_entry['facebook_user_cover_source'],
                    'facebook_user_about':              facebook_user_entry['facebook_user_about'],
                    'facebook_user_is_verified':        facebook_user_entry['facebook_user_is_verified'],
                    'facebook_user_friend_total_count': facebook_user_entry['facebook_user_friend_total_count'],
                }
            )
            facebook_user_saved = True
            success = True
            status = "FACEBOOK_USERS_CREATED"
        except Exception as e:
            facebook_user_saved = False
            facebook_user = FacebookUser()
            success = False
            status = "FACEBOOK_USERS_NOT_CREATED"
        results = {
            'success':              success,
            'status':               status,
            'facebook_user_saved':  facebook_user_saved,
            'facebook_user':        facebook_user,
            }
        return results

    def retrieve_facebook_auth_response(self, voter_device_id):
        """

        :param voter_device_id:
        :return:
        """
        facebook_auth_response = FacebookAuthResponse()
        facebook_auth_response_id = 0

        try:
            if positive_value_exists(voter_device_id):
                facebook_auth_response = FacebookAuthResponse.objects.get(
                    voter_device_id__iexact=voter_device_id,
                )
                facebook_auth_response_id = facebook_auth_response.id
                facebook_auth_response_found = True
                success = True
                status = "RETRIEVE_FACEBOOK_AUTH_RESPONSE_FOUND_BY_VOTER_DEVICE_ID"
            else:
                facebook_auth_response_found = False
                success = False
                status = "RETRIEVE_FACEBOOK_AUTH_RESPONSE_VARIABLES_MISSING"
        except FacebookAuthResponse.DoesNotExist:
            facebook_auth_response_found = False
            success = True
            status = "RETRIEVE_FACEBOOK_AUTH_RESPONSE_NOT_FOUND"
        except Exception as e:
            facebook_auth_response_found = False
            success = False
            status = 'FAILED retrieve_facebook_auth_response'

        results = {
            'success': success,
            'status': status,
            'facebook_auth_response_found': facebook_auth_response_found,
            'facebook_auth_response_id': facebook_auth_response_id,
            'facebook_auth_response': facebook_auth_response,
        }
        return results

    def fetch_facebook_id_from_voter_we_vote_id(self, voter_we_vote_id):
        facebook_user_id = 0
        facebook_results = self.retrieve_facebook_link_to_voter(facebook_user_id, voter_we_vote_id)
        if facebook_results['facebook_link_to_voter_found']:
            facebook_link_to_voter = facebook_results['facebook_link_to_voter']
            facebook_user_id = facebook_link_to_voter.facebook_user_id
        return facebook_user_id

    def retrieve_facebook_link_to_voter_from_voter_we_vote_id(self, voter_we_vote_id):
        facebook_user_id = 0
        facebook_secret_key = ""
        return self.retrieve_facebook_link_to_voter(facebook_user_id, voter_we_vote_id, facebook_secret_key)

    def retrieve_facebook_link_to_voter_from_facebook_secret_key(self, facebook_secret_key):
        facebook_user_id = 0
        voter_we_vote_id = ""
        return self.retrieve_facebook_link_to_voter(facebook_user_id, voter_we_vote_id, facebook_secret_key)

    def retrieve_facebook_link_to_voter(self, facebook_user_id=0, voter_we_vote_id='', facebook_secret_key=''):
        """

        :param facebook_user_id:
        :param voter_we_vote_id:
        :param facebook_secret_key:
        :return:
        """
        facebook_link_to_voter = FacebookLinkToVoter()
        facebook_link_to_voter_id = 0

        try:
            if positive_value_exists(facebook_user_id):
                facebook_link_to_voter = FacebookLinkToVoter.objects.get(
                    facebook_user_id=facebook_user_id,
                )
                facebook_link_to_voter_id = facebook_link_to_voter.id
                facebook_link_to_voter_found = True
                success = True
                status = "RETRIEVE_FACEBOOK_LINK_TO_VOTER_FOUND_BY_FACEBOOK_USER_ID"
            elif positive_value_exists(voter_we_vote_id):
                facebook_link_to_voter = FacebookLinkToVoter.objects.get(
                    voter_we_vote_id__iexact=voter_we_vote_id,
                )
                facebook_link_to_voter_id = facebook_link_to_voter.id
                facebook_link_to_voter_found = True
                success = True
                status = "RETRIEVE_FACEBOOK_LINK_TO_VOTER_FOUND_BY_VOTER_WE_VOTE_ID"
            elif positive_value_exists(facebook_secret_key):
                facebook_link_to_voter = FacebookLinkToVoter.objects.get(
                    secret_key=facebook_secret_key,
                )
                facebook_link_to_voter_id = facebook_link_to_voter.id
                facebook_link_to_voter_found = True
                success = True
                status = "RETRIEVE_FACEBOOK_LINK_TO_VOTER_FOUND_BY_FACEBOOK_SECRET_KEY"
            else:
                facebook_link_to_voter_found = False
                success = False
                status = "RETRIEVE_FACEBOOK_LINK_TO_VOTER_VARIABLES_MISSING"
        except FacebookLinkToVoter.DoesNotExist:
            facebook_link_to_voter_found = False
            success = True
            status = "RETRIEVE_FACEBOOK_LINK_TO_VOTER_NOT_FOUND"
        except Exception as e:
            facebook_link_to_voter_found = False
            success = False
            status = 'FAILED retrieve_facebook_link_to_voter'

        results = {
            'success': success,
            'status': status,
            'facebook_link_to_voter_found': facebook_link_to_voter_found,
            'facebook_link_to_voter_id': facebook_link_to_voter_id,
            'facebook_link_to_voter': facebook_link_to_voter,
        }
        return results

    def extract_facebook_details_data(self, facebook_friend_api_details_entry):
        """
        Extracting facebook friend details with required fields
        :param facebook_friend_api_details_entry:
        :return:
        """
        facebook_friend_dict = {}
        facebook_friend_dict['facebook_user_id'] = (facebook_friend_api_details_entry.get('id')
                                                    if 'id' in facebook_friend_api_details_entry.keys() else None)
        facebook_friend_dict['facebook_user_name'] = (facebook_friend_api_details_entry.get('name')
                                                      if 'name' in facebook_friend_api_details_entry.keys() else "")
        facebook_friend_dict['facebook_user_first_name'] = (facebook_friend_api_details_entry.get('first_name')
                                                            if 'first_name' in facebook_friend_api_details_entry.keys()
                                                            else "")
        facebook_friend_dict['facebook_user_middle_name'] = (facebook_friend_api_details_entry.get('middle_name')
                                                             if 'middle_name' in facebook_friend_api_details_entry.
                                                             keys() else "")
        facebook_friend_dict['facebook_user_last_name'] = (facebook_friend_api_details_entry.get('last_name')
                                                           if 'last_name' in facebook_friend_api_details_entry.keys()
                                                           else "")
        facebook_friend_dict['facebook_user_location_id'] = (facebook_friend_api_details_entry.get('location').get('id')
                                                             if 'location' in facebook_friend_api_details_entry.keys()
                                                                and facebook_friend_api_details_entry.
                                                             get('location', {}).get('id', {}) else None)
        facebook_friend_dict['facebook_user_location_name'] = (facebook_friend_api_details_entry.get('location').get(
            'name') if 'location' in facebook_friend_api_details_entry.keys() and facebook_friend_api_details_entry.get(
            'location', {}).get('name', {}) else "")
        facebook_friend_dict['facebook_user_gender'] = (facebook_friend_api_details_entry.get('gender')
                                                        if 'gender' in facebook_friend_api_details_entry.keys() else "")
        facebook_friend_dict['facebook_user_birthday'] = (facebook_friend_api_details_entry.get('birthday')
                                                          if 'birthday' in facebook_friend_api_details_entry.keys()
                                                          else "")
        facebook_friend_dict['facebook_user_cover_source'] = (facebook_friend_api_details_entry.get('cover').get(
            'source') if 'cover' in facebook_friend_api_details_entry.keys() and facebook_friend_api_details_entry.get(
            'cover', {}).get('source', {}) else "")
        facebook_friend_dict['facebook_user_about'] = (facebook_friend_api_details_entry.get('about')
                                                       if 'about' in facebook_friend_api_details_entry.keys() else "")
        facebook_friend_dict['facebook_user_is_verified'] = (facebook_friend_api_details_entry.get('is_verified')
                                                             if 'is_verified' in facebook_friend_api_details_entry.
                                                             keys() else "")
        return facebook_friend_dict

    def retrieve_facebook_friends_from_facebook(self, voter_device_id):
        """
        We use this routine to retrieve my facebook friends details and updating FacebookFriendsOfMe table
        :param voter_device_id:
        :return: facebook_friends_list
        """
        success = False
        status = ''
        facebook_friends_list_found = False
        facebook_users_list = []
        # required fields need to be updated in FacebookUser table
        facebook_api_fields = "id, name, first_name, middle_name, last_name, location{id, name}, gender, birthday, " \
                              "cover{source}, about, is_verified, friends{id, name, first_name, middle_name, " \
                              "last_name, location{id, name}, gender, birthday, cover{source}, about, is_verified} "
        auth_response_results = self.retrieve_facebook_auth_response(voter_device_id)
        if not auth_response_results['facebook_auth_response_found']:
            error_results = {
                'status':                       "FACEBOOK_AUTH_RESPONSE_NOT_FOUND",
                'success':                      success,
                'facebook_friends_list_found':  facebook_friends_list_found,
                'facebook_users_list':          facebook_users_list,
            }
            return error_results

        facebook_auth_response = auth_response_results['facebook_auth_response']
        try:
            facebook_graph = facebook.GraphAPI(facebook_auth_response.facebook_access_token, version='2.8')
            facebook_friends_api_details = facebook_graph.get_connections(id=facebook_auth_response.facebook_user_id,
                                                                 connection_name="friends", fields=facebook_api_fields)

            # graph.get_connections returns three dictionary keys i.e. data, paging, summary,
            # here data key contains list of friends with the given fields values and paging contains cursors positions
            # and summary contains total_count of your friends, for ex:
            # {"data": [{"name": "Micheal", "first_name": "Micheal", "id": "16086981492"},
            # {"name": "John", "first_name": "John", "id": "1263984"],
            # "paging": {"cursors": {"before": "QVFmc0QVBsZAk1KWmNwRVFoRzB1MGFDWlpoa3J0NFR6VTQZD",
            # "after": "QVFIUlAzdGplaWV5YTZAmeUNCNzVuRk1iPZAnhUNjltUldoSjR5aWZAxdGJ2UktEUHQzNWpBeHRmcEkZD"}},
            # "summary": {'total_count': 10}}
            for facebook_friend_api_details_entry in facebook_friends_api_details.get('data', []):
                # Extract required details for each facebook friend and then updating FacebookFriendsOfMe table
                facebook_friend_dict = self.extract_facebook_details_data(facebook_friend_api_details_entry)
                facebook_friend_dict['facebook_user_friend_total_count'] = (
                    facebook_friend_api_details_entry.get('friends').get('summary').get('total_count')
                    if facebook_friend_api_details_entry.get('friends', {}).get('summary', {}).get('total_count', {})
                    else None)
                facebook_users_list.append(facebook_friend_dict)
                facebook_friends_saved_results = self.create_or_update_facebook_friends_of_me(
                    facebook_auth_response.facebook_user_id, facebook_friend_dict.get('facebook_user_id'))
                status += ' ' + facebook_friends_saved_results['status']

                # Extract Friend's friend details
                if facebook_friend_api_details_entry.get('friends', {}).get('data', []):
                    for facebook_friends_friend_details_entry in \
                            facebook_friend_api_details_entry.get('friends', {}).get('data', []):
                        facebook_friends_friend_dict = self.extract_facebook_details_data(
                            facebook_friends_friend_details_entry)
                        facebook_friends_friend_dict['facebook_user_friend_total_count'] = None
                        facebook_users_list.append(facebook_friends_friend_dict)

            success = True
            status += " " + "FACEBOOK_FRIENDS_LIST_FOUND"
            facebook_friends_list_found = True
        except Exception as e:
            success = False
            status += " " + "FACEBOOK_FRIENDS_LIST_NOT_FOUND"
            facebook_friends_list_found = False

        results = {
            'success':                      success,
            'status':                       status,
            'facebook_friends_list_found':  facebook_friends_list_found,
            'facebook_users_list':          facebook_users_list,
        }
        return results

    def retrieve_facebook_friends_of_me_list(self, facebook_id_of_me):
        """
        Reterive my friends facebook ids from FacebookFriendsOfMe table.
        :param facebook_id_of_me:
        :return:
        """
        status = ""
        facebook_friends_of_me_list = []

        if not positive_value_exists(facebook_id_of_me):
            success = False
            status = 'RETRIEVE_FACEBOOK_FRIENDS_OF_ME-MISSING_FACEBOOK_ID '
            results = {
                'success':                              success,
                'status':                               status,
                'facebook_friends_of_me_list_found':    False,
                'facebook_friends_of_me_list':          [],
            }
            return results

        try:
            facebook_friends_of_me_queryset = FacebookFriendsOfMe.objects.all()
            facebook_friends_of_me_queryset = facebook_friends_of_me_queryset.filter(
                facebook_id_of_me=facebook_id_of_me)
            facebook_friends_of_me_list = facebook_friends_of_me_queryset

            if len(facebook_friends_of_me_list):
                success = True
                facebook_friends_of_me_list_found = True
                status += ' FACEBOOK_FRIENDS_OF_ME_LIST_RETRIEVED '
            else:
                success = True
                facebook_friends_of_me_list_found = False
                status += ' NO_FACEBOOK_FRIENDS_OF_ME_LIST_RETRIEVED '
        except FacebookFriendsOfMe.DoesNotExist:
            # No data found. Not a problem.
            success = True
            facebook_friends_of_me_list_found = False
            status += ' NO_FACEBOOK_FRIENDS_OF_ME_LIST_RETRIEVED_DoesNotExist '
            facebook_friends_of_me_list = []
        except Exception as e:
            success = False
            facebook_friends_of_me_list_found = False
            status += ' FAILED retrieve_facebook_friends_of_me_list FacebookFriendsOfMe '

        results = {
            'success':                              success,
            'status':                               status,
            'facebook_friends_of_me_list_found':    facebook_friends_of_me_list_found,
            'facebook_friends_of_me_list':          facebook_friends_of_me_list,
        }
        return results

    def retrieve_facebook_user_list(self, facebook_id_of_me):
        """
        Reterive facebook user ids from FacebookUser table.
        :param facebook_id_of_me:
        :return:
        """
        status = ""
        facebook_user_list = []

        if not positive_value_exists(facebook_id_of_me):
            success = False
            status = 'RETRIEVE_FACEBOOK_USERS-MISSING_FACEBOOK_ID '
            results = {
                'success':                  success,
                'status':                   status,
                'facebook_user_list_found': False,
                'facebook_user_list':       [],
            }
            return results

        try:
            facebook_user_queryset = FacebookUser.objects.all()
            facebook_user_queryset = facebook_user_queryset.filter(
                facebook_id_of_me=facebook_id_of_me)
            facebook_user_list = facebook_user_queryset

            if len(facebook_user_list):
                success = True
                facebook_user_list_found = True
                status += ' FACEBOOK_USER_LIST_RETRIEVED '
            else:
                success = True
                facebook_user_list_found = False
                status += ' NO_FACEBOOK_USER_LIST_RETRIEVED '
        except FacebookUser.DoesNotExist:
            # No data found. Not a problem.
            success = True
            facebook_user_list_found = False
            status += ' NO_FACEBOOK_USER_LIST_RETRIEVED_DoesNotExist '
            facebook_user_list = []
        except Exception as e:
            success = False
            facebook_user_list_found = False
            status += ' FAILED retrieve_facebook_user_list FacebookUser '

        results = {
            'success':                     success,
            'status':                      status,
            'facebook_user_list_found':    facebook_user_list_found,
            'facebook_user_list':          facebook_user_list,
        }
        return results
