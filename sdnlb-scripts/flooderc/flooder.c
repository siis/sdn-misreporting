/**
 * File: flooder.c
 *
 * Description   : Traffic source for sdnlb.
 * Date          : January 2020
 * Last Modified : July 2020
 */

/* Include Files  */
#include <pcap.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdbool.h>

#include <sys/socket.h>
#include <arpa/inet.h>

#include <netdb.h>
#include <linux/ip.h>
#include <linux/icmp.h>
#include <net/if.h>
#include <netinet/ether.h>

#include <unistd.h>

#include <pthread.h>

/* Project Includes  */

/* Globals */
int pkts_added = 0;
long total_pkt_size = 0;
int num_pkts = 0;
struct pkt_node **pkt_list = NULL;
struct active_flow **active_flows_list = NULL;
int num_active_flows = 0;
pthread_mutex_t active_list_lock;
pthread_mutex_t num_active_flows_lock;
pthread_mutex_t flooder_handle_lock;

/* Definitions  */

struct pkt_node
{
    u_char *eth_pkt;
    int length;
};

struct active_flow
{
    struct pkt_node *pnode;
    float duration;
    int time_active;
    time_t start_time;
};

struct active_flow_node_t
{
    struct active_flow *af;
    struct active_flow_node_t *next;
    struct active_flow_node_t *prev;
} * head; // ** linked list of flow nodes (which contain pkt, duration, etc)

void push(struct active_flow **af)
{
    struct active_flow_node_t *current = NULL;

    if (head == NULL)
    {
        current = (struct active_flow_node_t *)malloc(sizeof(struct active_flow_node_t));
        current->af = *af;
        current->next = NULL;
        current->prev = NULL;
        head = current;
        return;
    }

    current = head;
    while (current->next != NULL)
    {
        current = current->next;
    }

    /* now we can add a new variable */
    current->next = (struct active_flow_node_t *)malloc(sizeof(struct active_flow_node_t));
    current->next->af = *af;
    current->next->next = NULL;
    current->next->prev = current;
}

void *remove_afnode(struct active_flow_node_t *afnode)
{
    struct active_flow_node_t *temp_node = NULL;
    if (afnode == head)
    {
        temp_node = head->next;
        free(head); // could maybe return this instead of freeing it
        head = temp_node;
        if (head != NULL)
        {
            head->prev = NULL;
        }
        return NULL;
    }
    // connect neighbors of afnode
    afnode->prev->next = afnode->next;
    afnode->next->prev = afnode->prev;
    free(afnode);
    return NULL;
}

struct active_flow_node_t *search_by_index(int n, int remove)
{
    struct active_flow_node_t *current = NULL;
    struct active_flow_node_t *temp_node = NULL;

    if (n == 0)
    {
        if (remove == 1)
        {
            temp_node = head->next;
            free(head); // could maybe return this instead of freeing it
            head = temp_node;
            head->prev = NULL;
            return NULL;
        }
        return head;
    }

    current = head;
    for (int i = 0; i < n - 1; i++)
    {
        if (current->next == NULL)
        {
            printf("Not enough nodes to get to index [%d]", n);
            return NULL;
        }
        current = current->next;
    }

    if (remove == 1)
    {
        // connect neighbors of current
        current->prev->next = current->next;
        current->next->prev = current->prev;
        free(current);
        return NULL;
    }
    return current;
}

/* Functions  */
void pkt_handler(u_char *args, const struct pcap_pkthdr *pkt_hdr, const u_char *pkt)
{
    int data_sz = 1500 - sizeof(struct ether_header) - pkt_hdr->len; // extra data
    char *data = NULL;
    if (data_sz > 0)
    { // if space left in pkt, pad to 1500
        data = (char *)calloc(data_sz, 1);
        memset(data, 0x1, data_sz - 1);
        data[data_sz - 1] = '\0';
    }
    else
    {
        data_sz = 0; // dont let it be negative, messes up the length fields and avg pkt size calculation
    }

    u_char *eth_pkt = (u_char *)calloc(1, sizeof(struct ether_header) + pkt_hdr->len + data_sz);
    struct ether_header *eh = (struct ether_header *)eth_pkt;
    eh->ether_type = htons(ETH_P_IP);
    int shost0 = 0xba; // still truncated even with this
    int shost1 = 0x6e;
    int shost2 = 0xd9;
    int shost3 = 0xe7;
    int shost4 = 0x7a;
    int shost5 = 0x30;
    eh->ether_shost[0] = shost0;
    eh->ether_shost[1] = shost1;
    eh->ether_shost[2] = shost2;
    eh->ether_shost[3] = shost3;
    eh->ether_shost[4] = shost4;
    eh->ether_shost[5] = shost5;
    int dhost0 = 0x12; // still truncated even with this
    int dhost1 = 0x34;
    int dhost2 = 0x56;
    int dhost3 = 0x78;
    int dhost4 = 0x90;
    int dhost5 = 0x12;
    eh->ether_dhost[0] = dhost0;
    eh->ether_dhost[1] = dhost1;
    eh->ether_dhost[2] = dhost2;
    eh->ether_dhost[3] = dhost3;
    eh->ether_dhost[4] = dhost4;
    eh->ether_dhost[5] = dhost5;

    pkt_list[pkts_added] = (struct pkt_node *)calloc(1, sizeof(struct pkt_node));
    pkt_list[pkts_added]->eth_pkt = eth_pkt;                                                // point node to the empty pkt in memory
    memcpy(pkt_list[pkts_added]->eth_pkt + sizeof(struct ether_header), pkt, pkt_hdr->len); // copy pkt contents into node (only pkt_hdr->len bytes of pkt)
    if (data_sz > 0)
    {
        // only copy pad data if necessary
        memcpy(pkt_list[pkts_added]->eth_pkt + sizeof(struct ether_header) + pkt_hdr->len, data, data_sz);
    }
    pkt_list[pkts_added]->length = sizeof(struct ether_header) + pkt_hdr->len + data_sz; // will send ether header plus IP pkt content
    pkts_added++;
    total_pkt_size += pkt_hdr->len + data_sz;
}

void *new_flows_runner(void *fh)
{
    struct timeval tv_start;
    pcap_t *flooder_handle = *((pcap_t **)fh);
    struct active_flow *af = NULL;
    for (int i = 0; i < num_pkts; i++)
    {
        pthread_mutex_lock(&flooder_handle_lock);
        pcap_inject(flooder_handle, pkt_list[i]->eth_pkt, pkt_list[i]->length); // inject once then add to active list
        pthread_mutex_unlock(&flooder_handle_lock);
        pthread_mutex_lock(&active_list_lock);

        af = (struct active_flow *)calloc(1, sizeof(struct active_flow));
        af->duration = 1; // *** secs
        af->time_active = 0;
        gettimeofday(&tv_start, NULL);
        af->start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
        af->pnode = pkt_list[i];
        push(&af);
        pthread_mutex_unlock(&active_list_lock);
        pthread_mutex_lock(&num_active_flows_lock);
        num_active_flows++;
        pthread_mutex_unlock(&num_active_flows_lock);

        usleep(10000); // 1/10000us=100pps, etc
    }

    return NULL;
}

void *active_flows_runner(void *fh)
{
    pcap_t *flooder_handle = *((pcap_t **)fh);
    uint64_t i = (uint64_t)0;

    struct timeval tv2_end;
    double tmp_dur = 0.0;
    double avg_flow_dur = 0.0;
    int num_flows_expired = 0;

    printf("Starting active runner [%d flows]...\n", num_active_flows);
    while (1)
    {
        pthread_mutex_lock(&active_list_lock);
        struct active_flow_node_t *inode = NULL;
        if (num_active_flows == 0)
        {
            i = 0;
            inode = search_by_index(i, 0);
            if (inode == NULL)
            { // new runner didnt get to add the flow yet (active runner moving quicker)
                pthread_mutex_unlock(&active_list_lock);
                continue; // just keep looping until we have an active flow
            }
        }
        else
        {
            i = rand() % num_active_flows;
            inode = search_by_index(i, 0);
            while ((inode == NULL) || (inode->af->pnode == NULL))
            {
                i = (rand() * rand()) % num_active_flows; // goes up to like 32k*32k = 1B, which should be more than enough
                inode = search_by_index(i, 0);
            }
        }

        pthread_mutex_unlock(&active_list_lock);
        pthread_mutex_lock(&flooder_handle_lock);
        pcap_inject(flooder_handle, inode->af->pnode->eth_pkt, inode->af->pnode->length); // *** send pkt out nic
        pthread_mutex_unlock(&flooder_handle_lock);
        inode->af->time_active++;
        pthread_mutex_lock(&num_active_flows_lock);
        pthread_mutex_unlock(&num_active_flows_lock); // dont sleep while holding lock

        if (inode->af->time_active >= inode->af->duration) // if last pkt for the flow was already sent, expire it
        {
            pthread_mutex_lock(&active_list_lock);
            inode->af->pnode = NULL; // expire the flow

            gettimeofday(&tv2_end, NULL);
            tmp_dur = (((tv2_end.tv_sec * 1e6) + tv2_end.tv_usec) - inode->af->start_time) / 1e6;
            remove_afnode(inode);
            pthread_mutex_unlock(&active_list_lock);

            pthread_mutex_lock(&num_active_flows_lock);
            num_flows_expired++;
            avg_flow_dur = ((avg_flow_dur * (num_flows_expired - 1)) + tmp_dur) * 1.0 / num_flows_expired;
            num_active_flows--;
            printf("\rAvg duration: %.2fs, tmp_dur: %.3fs, Num_active_flows: %d ", avg_flow_dur, tmp_dur, num_active_flows);
            pthread_mutex_unlock(&num_active_flows_lock);
        }

        usleep((int)1e6 / num_active_flows); // send out 1 pkt for each active flow
    }
}

int run_flooder()
{
    // record number of packets in pcap and init packet array
    num_pkts = (int)1.0e6;
    pkt_list = (struct pkt_node **)calloc(num_pkts, sizeof(struct pkt_node *));
    active_flows_list = (struct active_flow **)calloc(num_pkts, sizeof(struct active_flow *));

    // init structures
    char *f = "../flooder-long-1.00M-flows.pcap";
    char error_buf1[PCAP_ERRBUF_SIZE];
    pcap_t *pcap_file_handle = pcap_open_offline(f, error_buf1);
    struct timeval tv_start;
    struct timeval tv2_end;
    double start_time = 0.0;
    double end_time = 0.0;

    // Step 1 - Read pcap from file
    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    pcap_loop(pcap_file_handle, num_pkts, pkt_handler, NULL);
    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Read pcap in %.3fs]\n", (end_time - start_time) / 1e6); // back to seconds
    printf("Packets read: %d\n", pkts_added);
    printf("Avg pkt size: %.3f bytes\n", total_pkt_size * 1.0 / num_pkts);
    pcap_close(pcap_file_handle); // close this handle for the pcap file

    // Step 2 - Flood pkts
    char error_buf2[PCAP_ERRBUF_SIZE];
    const char *dev = "uph-eth0";
    int snaplen = BUFSIZ;
    int promisc = 0;
    int timeout_lim = 10000;                                                                 // in ms
    pcap_t *flooder_handle = pcap_open_live(dev, snaplen, promisc, timeout_lim, error_buf2); // open new pcap handle for nic
    if (flooder_handle == NULL)
    {
        printf("Error finding device: %s\n", error_buf2);
        return -1;
    }

    start_time = 0.0;
    end_time = 0.0;
    gettimeofday(&tv_start, NULL);
    start_time = (tv_start.tv_sec * 1e6) + tv_start.tv_usec;
    pthread_t new_flows_thread;
    pthread_t active_flows_thread;
    pthread_create(&new_flows_thread, NULL, new_flows_runner, &flooder_handle);       // *** send new flows
    pthread_create(&active_flows_thread, NULL, active_flows_runner, &flooder_handle); // *** send active flows
    pthread_join(new_flows_thread, NULL);
    pthread_join(active_flows_thread, NULL);

    gettimeofday(&tv2_end, NULL);
    end_time = (tv2_end.tv_sec * 1e6) + tv2_end.tv_usec;
    printf("[Flooded packets in %.3fs]\n", (end_time - start_time) / 1e6);
    pcap_close(flooder_handle); // close this handle for the flooder

    return 0;
}

int main(int argc, char *argv[])
{
    if (pthread_mutex_init(&num_active_flows_lock, NULL) != 0)
    {
        printf("error on init active_flows_lock\n");
        return -1;
    }

    if (pthread_mutex_init(&active_list_lock, NULL) != 0)
    {
        printf("error on init active_list_lock\n");
        return -1;
    }

    if (pthread_mutex_init(&flooder_handle_lock, NULL) != 0)
    {
        printf("error on init flooder_handle_lock\n");
        return -1;
    }

    srand(time(NULL));
    run_flooder();
}
